"""v6 earnings engine, SHADOW MODE. Never publishes, never touches the site, V5, Market Views or Track Record.

Run shortly after the US open (e.g. 14:00 UTC). For companies on the Nasdaq earnings calendar of the previous session that have
EPS and consensus, it fetches daily bars (Yahoo, free, no key) including today's open, computes the same point-in-time features as the
backtest (tools/v6/earnings_dataset.features), scores the frozen shadow model (model-v6e-shadow.*) and appends one frozen record per
event to research/v6/shadow/earnings-calls.jsonl (append-only; an id is never written twice).
Tiers: priority = top-10% margin, view = top-30% margin (both thresholds from 2024 validation), else none (No View).
Entry used for later scoring = first daily open after frozen_at (the next session's open) - stricter than the backtest's same-open entry,
because the shadow call is frozen after today's open has printed. Outcomes are resolved by --resolve (next-open to following-open,
vs the median liquid stock), kept separate from the backtest.
  python3 -m tools.v6.shadow_earnings [--resolve] [--day YYYY-MM-DD]"""
import argparse, json, math, os, statistics, time, urllib.request
from datetime import datetime, timezone, timedelta
import lightgbm as lgb, numpy as np
from tools.v6.earnings_dataset import V6, OUT as DS, features, money
from tools.v6.earnings_model import FEATS
SH = os.path.join(V6, 'shadow'); LEDGER = os.path.join(SH, 'earnings-calls.jsonl')
UA = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.load(r)


def bars(t, days=150):
    p2 = int(time.time()); p1 = p2 - days * 86400
    try: r = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(t)}?period1={p1}&period2={p2}&interval=1d')['chart']['result'][0]
    except Exception: return None
    q = r['indicators']['quote'][0]
    rows = [(datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d'), o, c, v) for ts, o, c, v in zip(r['timestamp'], q['open'], q['close'], q['volume']) if o and c]
    return {'dates': [x[0] for x in rows], 'o': [x[1] for x in rows], 'c': [x[2] for x in rows], 'v': [x[3] or 0 for x in rows]}


def ledger():
    try: return [json.loads(l) for l in open(LEDGER)]
    except FileNotFoundError: return []


def run(day=None):
    os.makedirs(SH, exist_ok=True)
    meta = json.load(open(os.path.join(DS, 'model-v6e-shadow.json'))); model = lgb.Booster(model_file=os.path.join(DS, meta['model']))
    spy, vix = bars('SPY'), bars('^VIX')
    if not spy: print('no SPY bars'); return
    today = spy['dates'][-1]; i_spy = len(spy['dates']) - 1
    day = day or spy['dates'][-2]  # previous session = report day
    if today <= day: print('entry session not open yet'); return
    rows = (get(f'https://api.nasdaq.com/api/calendar/earnings?date={day}').get('data') or {}).get('rows') or []
    done = {r['id'] for r in ledger()}; now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); n = 0
    with open(LEDGER, 'a') as out:
        for r in rows:
            t = r.get('symbol') or ''; eps, est = money(r.get('eps')), money(r.get('epsForecast'))
            rid = f'{t}:{day}'
            if rid in done or not t.isalpha() or eps is None or est is None: continue
            P = bars(t)
            if not P or len(P['dates']) < 80 or P['dates'][-1] != today or P['dates'][-2] != day and P['dates'][-2] > day: continue
            i = len(P['dates']) - 1
            f, sig = features(P, spy, vix, i, i_spy, {'eps': eps, 'est': est, 'n_est': int(r.get('noOfEsts') or 0) if str(r.get('noOfEsts') or '').isdigit() else 0}, None)
            if f is None: continue
            p = float(model.predict(np.array([[f[k] for k in FEATS]]))[0]); m = abs(p - .5)
            tier = 'priority' if m >= meta['priority_margin_top10'] else 'view' if m >= meta['view_margin_top30'] else 'none'
            out.write(json.dumps({'id': rid, 'engine': meta['version'], 'shadow': True, 'ticker': t, 'report_day': day, 'frozen_at': now, 'p_up': round(p, 4),
                                  'direction': ('long' if p > .5 else 'short') if tier != 'none' else 'none', 'tier': tier, 'features': f, 'sigma': sig,
                                  'entry_rule': 'first daily open after frozen_at; exit next open; vs median liquid stock'}) + '\n'); n += 1
    print(f'{day}: {len(rows)} calendar rows, {n} shadow records frozen')


def resolve():
    L = ledger(); res_path = os.path.join(SH, 'earnings-outcomes.json')
    try: R = json.load(open(res_path))
    except FileNotFoundError: R = {}
    spy = bars('SPY', 60) or {'dates': []}
    for r in L:
        if r['id'] in R or r['direction'] == 'none': continue
        P = bars(r['ticker'], 60)
        if not P: continue
        k = next((j for j, d in enumerate(P['dates']) if d > r['frozen_at'][:10]), None)
        if k is None or k + 1 >= len(P['dates']): continue
        raw = math.log(P['o'][k + 1] / P['o'][k])
        si = spy['dates'].index(P['dates'][k]) if P['dates'][k] in spy['dates'] else None
        if si is None or si + 1 >= len(spy['dates']) or spy['dates'][si + 1] != P['dates'][k + 1]: continue
        adj = raw - math.log(spy['o'][si + 1] / spy['o'][si])  # live proxy: SPY (the universe median needs the full price cache)
        res = 'flat' if abs(adj) < .25 * r['sigma'] else ('hit' if (adj > 0) == (r['direction'] == 'long') else 'miss')
        R[r['id']] = {'entry_day': P['dates'][k], 'exit_day': P['dates'][k + 1], 'adj_vs_spy': adj, 'res': res}
    json.dump(R, open(res_path, 'w'), indent=0)
    c = [v['res'] for v in R.values()]
    print(f"resolved {len(R)}: hits {c.count('hit')} misses {c.count('miss')} flat {c.count('flat')}")


if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('--resolve', action='store_true'); a.add_argument('--day'); x = a.parse_args()
    resolve() if x.resolve else run(x.day)
