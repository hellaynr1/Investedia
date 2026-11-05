"""v6 earnings-reaction dataset (point-in-time, no network, no paid APIs).

Events: Nasdaq earnings calendar rows (research/v6/earnings/YYYY-MM.json) with reported EPS and consensus, for tickers with a cached
daily price history (research/v6/prices). One event per (ticker, report date); same ticker within 20 sessions is collapsed to the first.

Timing (conservative because the calendar rarely says before-open/after-close):
  report date D. The call is made at the open of the first session strictly after D ("entry", D+1 open), which is after any
  pre-market (D) or after-hours (D) release. Exit is the next session's open (~24 h later, the live 24-hour rule). Every feature uses
  only bars that closed on or before D plus the entry-session open price itself (known at the call).
Label: return vs the median liquid stock over the same open->open window (tools/v6/universe_median.py); SPY-adjusted kept as adj_spy. |adj| < 0.25 x 20-day daily sigma = "flat"
(neutral, excluded from directional accuracy, reported separately). Split-adjusted series only; unadjusted series spanning a split
are dropped. Missing bars -> event dropped (counted in rejected).
  python3 -m tools.v6.earnings_dataset      -> research/v6/earnings-ds/dataset.jsonl.gz + coverage.json"""
import glob, gzip, json, math, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V6 = os.path.join(ROOT, 'research', 'v6'); OUT = os.path.join(V6, 'earnings-ds')
sys.path.insert(0, ROOT)
try: from engine.context import sector_etf
except Exception: sector_etf = lambda s: None


def money(s):
    if s in (None, '', 'N/A'): return None
    s = str(s).replace('$', '').replace(',', '').strip(); neg = s.startswith('(') and s.endswith(')')
    try: v = float(s.strip('()'))
    except ValueError: return None
    return -v if neg else v


def load_px(t):
    p = os.path.join(V6, 'prices', t.replace('^', '_') + '.json.gz')
    try: d = json.load(gzip.open(p))
    except Exception: return None
    if not d.get('split_adjusted', True) and d.get('splits'): return None
    rows = [r for r in d['d'] if r[1] and r[4] and r[1] > 0 and r[4] > 0]
    return {'dates': [r[0] for r in rows], 'o': [r[1] for r in rows], 'c': [r[4] for r in rows], 'v': [r[5] or 0 for r in rows]}


def idx_after(dates, day):
    """index of first session strictly after `day`"""
    lo, hi = 0, len(dates)
    while lo < hi:
        m = (lo + hi) // 2
        if dates[m] <= day: lo = m + 1
        else: hi = m
    return lo


def sd(xs):
    if len(xs) < 5: return None
    m = sum(xs) / len(xs); return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def features(P, spy, vix, i, si, e, last):
    """Point-in-time features for a call at the open of session i (P/spy index si). Uses closes up to session i-1 and the open of i only.
    Returns (features dict, sigma) or (None, None)."""
    d0 = i - 1
    o, c, v = P['o'], P['c'], P['v']
    rets = [math.log(c[k] / c[k - 1]) for k in range(d0 - 19, d0 + 1)]
    sig = sd(rets)
    if not sig or sig <= 0: return None, None
    so, sc = spy['o'], spy['c']
    lr = lambda a, b: math.log(b / a)
    react = lr(c[d0 - 1], c[d0]) - lr(sc[si - 2], sc[si - 1])
    gap = lr(c[d0], o[i]) - lr(sc[si - 1], so[si])
    mom5 = lr(c[d0 - 5], c[d0 - 1]) - lr(sc[si - 6], sc[si - 2])
    mom20 = lr(c[d0 - 20], c[d0 - 1]) - lr(sc[si - 21], sc[si - 2])
    mom60 = lr(c[d0 - 60], c[d0 - 1]) - lr(sc[si - 61], sc[si - 2])
    vol20 = sum(v[d0 - 20:d0]) / 20 or 1
    dv20 = sum(v[k] * c[k] for k in range(d0 - 20, d0)) / 20
    spy20 = lr(sc[si - 21], sc[si - 1]); spys = sd([lr(sc[k - 1], sc[k]) for k in range(si - 20, si)])
    vi = idx_after(vix['dates'], P['dates'][d0]) - 1 if vix else -1
    surprise = (e['eps'] - e['est']) / max(abs(e['est']), 0.05)
    pq = last['surprise'] if last and i - last['i'] < 90 else None
    return {'surprise': max(-3, min(3, surprise)), 'surp_pos': 1 if surprise > 0.005 else (-1 if surprise < -0.005 else 0), 'abs_surprise': min(3, abs(surprise)),
                          'eps_pos': 1 if e['eps'] > 0 else 0, 'log_n_est': math.log1p(e['n_est']), 'prev_surprise': max(-3, min(3, pq)) if pq is not None else 0.0, 'has_prev': 1 if pq is not None else 0,
                          'react_z': react / sig, 'gap_z': gap / sig, 'move_z': (react + gap) / sig, 'mom5_z': mom5 / sig, 'mom20': mom20, 'mom60': mom60,
                          'sigma20': sig, 'log_dvol': math.log1p(dv20), 'vol_ratio_d': (v[d0] / vol20) if vol20 else 1.0, 'spy20': spy20, 'spy_sig': spys or 0.0,
                          'vix': vix['c'][vi] if vix and vi >= 0 else 20.0}, sig


def main():
    os.makedirs(OUT, exist_ok=True)
    spy, vix = load_px('SPY'), load_px('^VIX')
    try: UM = json.load(open(os.path.join(OUT, 'universe-median.json')))
    except Exception: UM = {}
    sic = {}
    try: sic = {k: v.get('sic') for k, v in json.load(open(os.path.join(ROOT, 'docs', 'assets', 'globe', 'industries.json')))['by'].items()}
    except Exception: pass
    have = {os.path.basename(f)[:-8] for f in glob.glob(os.path.join(V6, 'prices', '*.json.gz'))}
    ev = []
    for f in sorted(glob.glob(os.path.join(V6, 'earnings', '*.json'))):
        for day, rows in json.load(open(f)).items():
            for r in rows or []:
                t = r.get('symbol') or ''
                if not re.fullmatch(r'[A-Z]{1,5}', t) or t not in have: continue
                eps, est = money(r.get('eps')), money(r.get('epsForecast'))
                if eps is None or est is None: continue
                ev.append({'t': t, 'day': day, 'eps': eps, 'est': est, 'n_est': int(r.get('noOfEsts') or 0) if str(r.get('noOfEsts') or '').isdigit() else 0,
                           'timing': r.get('time') or '', 'fq': r.get('fiscalQuarterEnding') or ''})
    ev.sort(key=lambda e: (e['t'], e['day']))
    cache, out, rej, prev = {}, [], {}, {}
    rj = lambda k: rej.__setitem__(k, rej.get(k, 0) + 1)
    for e in ev:
        t = e['t']
        if t not in cache: cache = {t: load_px(t)}  # one ticker at a time (sorted), small memory
        P = cache[t]
        if not P or len(P['dates']) < 80: rj('no-price-history'); continue
        i = idx_after(P['dates'], e['day'])  # entry session
        if i < 61 or i + 1 >= len(P['dates']): rj('outside-price-window'); continue
        last = prev.get(t)
        if last and i - last['i'] < 20: rj('duplicate-within-20-sessions'); continue
        d0 = i - 1  # last session on/before D
        if P['dates'][d0] < e['day'] and (P['dates'][i] > e['day']):  # D itself was not a session (weekend/holiday)
            pass
        # market alignment
        si = idx_after(spy['dates'], P['dates'][i]) - 1
        if si < 61 or si + 1 >= len(spy['dates']) or spy['dates'][si] != P['dates'][i] or spy['dates'][si + 1] != P['dates'][i + 1]: rj('calendar-mismatch'); continue
        f, sig = features(P, spy, vix, i, si, e, last)
        if f is None: rj('no-volatility'); continue
        o, so = P['o'], spy['o']; lr = lambda a, b: math.log(b / a)
        surprise = (e['eps'] - e['est']) / max(abs(e['est']), 0.05)
        etf = sector_etf(sic.get(t)) if sic.get(t) else None
        # label: entry open -> next open
        raw = lr(o[i], o[i + 1]); mkt = lr(so[si], so[si + 1]); adj_spy = raw - mkt
        if UM and P['dates'][i] not in UM: rj('no-universe-benchmark'); continue
        adj = raw - UM[P['dates'][i]] if UM else adj_spy  # primary: vs the median liquid stock that session
        sec_adj = None
        if etf:
            E = cache.setdefault('__' + etf, load_px(etf))
            if E:
                ei = idx_after(E['dates'], P['dates'][i]) - 1
                if 0 <= ei < len(E['dates']) - 1 and E['dates'][ei] == P['dates'][i] and E['dates'][ei + 1] == P['dates'][i + 1]: sec_adj = raw - lr(E['o'][ei], E['o'][ei + 1])
        res = 'flat' if abs(adj) < 0.25 * sig else ('up' if adj > 0 else 'down')
        out.append({'id': f"{t}:{e['day']}", 't': t, 'report_day': e['day'], 'entry_day': P['dates'][i], 'exit_day': P['dates'][i + 1], 'timing': e['timing'],
                    'f': f,
                    'y': {'raw': raw, 'mkt': mkt, 'adj': adj, 'adj_spy': adj_spy, 'res_spy': 'flat' if abs(adj_spy) < 0.25 * sig else ('up' if adj_spy > 0 else 'down'), 'sec_adj': sec_adj, 'res': res, 'sigma': sig}})
        prev[t] = {'i': i, 'surprise': surprise}
    with gzip.open(os.path.join(OUT, 'dataset.jsonl.gz'), 'wt') as f:
        for r in out: f.write(json.dumps(r, separators=(',', ':')) + '\n')
    yrs = {}
    for r in out: yrs[r['entry_day'][:4]] = yrs.get(r['entry_day'][:4], 0) + 1
    cov = {'events_in_calendar_with_prices': len(ev), 'events_kept': len(out), 'rejected': rej, 'by_year': yrs, 'tickers': len({r['t'] for r in out}),
           'labels': {k: sum(1 for r in out if r['y']['res'] == k) for k in ('up', 'down', 'flat')}, 'with_sector_label': sum(1 for r in out if r['y']['sec_adj'] is not None)}
    json.dump(cov, open(os.path.join(OUT, 'coverage.json'), 'w'), indent=1)
    print(json.dumps(cov, indent=1))


if __name__ == '__main__': main()
