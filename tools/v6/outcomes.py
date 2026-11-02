"""Pure Track D outcome calculation. No clock, network, or prediction mutation."""
import math
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo
from statistics import stdev
from engine import outcome as legacy
from engine.policy import meaningful

NY = ZoneInfo('America/New_York')
RULE = 'v6-research-daily-1'


def timestamp(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timezone required')
    return dt.astimezone(timezone.utc)


def cutoff(call):
    return max(timestamp(call[k]) for k in
               ('information_public_at', 'prediction_generated_at', 'public_call_at'))


def valid(value):
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def calculate_trades(call, bars, as_of):
    """Exact observed trades; delegates the frozen outcome-v4 horizon semantics."""
    end = timestamp(as_of).timestamp()
    clean = sorted({float(t): float(p) for t, p in bars if valid(p) and t <= end}.items())
    view = {'start_ts': cutoff(call).timestamp(), 'decision': call['direction'],
            'horizon': call['horizon'], 'cls': 'equity', 'context': call.get('context', {})}
    if call['direction'] == 'none':
        return {'res': 'no-view', 'rule': legacy.RULE}
    result = legacy.judge(view, clean, end)
    return result or {'res': 'pending', 'rule': legacy.RULE, 'why': 'entry or horizon not available'}


def session_time(day, hour, minute=0):
    return datetime.combine(datetime.fromisoformat(day).date(), time(hour, minute), NY).astimezone(timezone.utc)


def calculate_daily(call, prices, market, sector, as_of):
    """Observed SPY dates define sessions, including holidays. Never extrapolate."""
    now, start = timestamp(as_of), cutoff(call)
    out = {'res': 'pending', 'relative_res': None, 'rule': RULE,
           'entry_method': 'conservative-next-open-proxy', 'why': 'no entry data'}
    if call['direction'] == 'none':
        return {**out, 'res': 'no-view', 'why': 'abstained'}
    if call['horizon'] not in ('S1', 'S2'):
        raise ValueError('daily prices support S1/S2 only')
    sessions = sorted({r[0] for r in market.get('d', []) if session_time(r[0], 16) <= now})
    eligible = [d for d in sessions if session_time(d, 9, 30) > start]
    if not eligible:
        return {**out, 'res':'unresolved' if (now-start).days>7 else 'pending', 'why':'entry calendar unavailable'}
    entry_day = eligible[0]
    n = int(call['horizon'][1:])
    i = sessions.index(entry_day)
    if i + n >= len(sessions):
        return {**out, 'why': 'horizon not complete'}
    exit_day = sessions[i+n]
    out['label_end_at'] = session_time(exit_day, 16).isoformat()
    if (session_time(entry_day, 9, 30) - start).days > 7:
        return {**out, 'res': 'unresolved', 'why': 'entry calendar gap'}
    data = {r[0]: r for r in prices.get('d', [])}
    if any(d not in data or not valid(data[d][1]) or not valid(data[d][4]) for d in sessions[i:i+n+1]):
        return {**out, 'res': 'unresolved', 'why': 'missing session prices'}
    if prices.get('split_adjusted') is not True and any(entry_day < d <= exit_day for d, _ in prices.get('splits', [])):
        return {**out, 'res': 'unresolved', 'why': 'raw series crosses split'}
    e, x = data[entry_day][1], data[exit_day][4]
    mv = (x/e-1)*100
    prior = [d for d in sessions if session_time(d, 16) < start and d in data]
    returns = [(data[b][4]/data[a][4]-1)*100 for a,b in zip(prior, prior[1:])
               if valid(data[a][4]) and valid(data[b][4])][-20:]
    sigma = stdev(returns) if len(returns) == 20 else None
    threshold = meaningful(mv, 'equity', sigma, n)
    sign = 1 if call['direction'] == 'long' else -1
    def verdict(move, floor):
        return 'void' if abs(move)>50 else 'flat' if abs(move)<floor else 'hit' if move*sign>0 else 'miss'
    out['subsequent_prices'] = [data[d] for d in sessions[i:i+n+1]]
    out.update(res=verdict(mv, threshold), why=None, entry=[session_time(entry_day,9,30).isoformat(),e],
               exit=[session_time(exit_day,16).isoformat(),x], move_pct=mv, threshold_pct=threshold,
               sigma_daily=sigma, sigma_complete=sigma is not None)
    bench = {r[0]: r for r in (sector or {}).get('d', [])}
    paired = [d for d in prior if d in bench and valid(bench[d][4])][-21:]
    if (len(paired)==21 and entry_day in bench and exit_day in bench
            and valid(bench[entry_day][1]) and valid(bench[exit_day][4])):
        excess = [(data[b][4]/data[a][4]-bench[b][4]/bench[a][4])*100 for a,b in zip(paired,paired[1:])]
        sm = (bench[exit_day][4]/bench[entry_day][1]-1)*100
        rel, floor = mv-sm, .5*stdev(excess)*math.sqrt(n)
        out.update(sector_move_pct=sm, relative_move_pct=rel, relative_threshold_pct=floor,
                   relative_res=verdict(rel, max(floor, 1e-12)))
    return out
