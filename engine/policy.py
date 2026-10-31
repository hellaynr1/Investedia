"""Frozen v4 tables and decision policy (research/ENGINE-V4.md §4-§8, §10). Changing anything here = a new engine version.
Pure functions: no network, no clock. decide() turns an extracted event + asset + market context into Long / Short / No call."""
import hashlib, json, math

ENGINE = 'pe-v4'
OUTCOME_RULE = 'outcome-v4'
TYPES = ['earnings', 'guidance', 'm&a', 'financing', 'analyst', 'product', 'legal-regulatory', 'management', 'macro-data',
         'central-bank', 'geopolitical', 'commodity-supply', 'trade-tariff', 'crypto', 'other']
CLASSES = ['equity', 'index', 'fx', 'commodity', 'crypto']
# §5 horizons: S1/S2 = close of the 1st/2nd full session after entry; 'Nh' = hours (24/7, near-24 h markets); None = no calls
H = {'earnings': ('S1', 'S1', None, None, None), 'guidance': ('S1', 'S1', None, None, None), 'financing': ('S1', 'S1', None, None, None),
     'management': ('S1', 'S1', None, None, None), 'm&a': ('S1', None, None, None, None), 'analyst': ('S2', None, None, None, None),
     'product': ('S1', None, None, None, '24h'), 'legal-regulatory': ('S1', None, None, None, '24h'),
     'macro-data': ('S1', 'S1', '6h', '6h', '6h'), 'central-bank': ('S1', 'S1', '24h', '24h', '24h'),
     'geopolitical': ('S2', 'S2', '48h', '48h', '48h'), 'trade-tariff': ('S2', 'S2', '48h', '48h', '48h'),
     'commodity-supply': ('S2', 'S2', '48h', '48h', None), 'crypto': (None, None, None, None, '24h'),
     'other': ('S1', 'S1', '24h', '24h', '24h')}
ACQUIRER_HORIZON = 'S2'
FLOOR = {'equity': .3, 'index': .2, 'fx': .1, 'commodity': .3, 'crypto': .5}           # §10 class floors, % move
SURPRISE_FLOOR = {'eps': 2.0, 'revenue': 2.0, 'guidance': 1.0, 'rate_bp': 10.0}         # §7, % (rates in bp)
DIRECT = {'subject', 'target', 'acquirer', 'counterparty', 'policy-rate', 'commodity-output', 'issuer'}
ALREADY_MOVED_SIGMA = 1.5
POINTS = {'expectations': 2, 'big_surprise': 1, 'direct': 1, 'single_catalyst': 1, 'context_agrees': 1, 'stance_agrees': 1}
NEEDS_EXPECTATIONS = {'earnings', 'guidance', 'macro-data', 'central-bank'}
REASONS = ['commentary', 'preview', 'price-move-recap', 'indirect', 'competing-catalysts', 'stance-neutral', 'no-expectations',
           'already-moved', 'unsupported-combination', 'duplicate-event', 'below-threshold']
POLICY_ID = hashlib.sha1(json.dumps([TYPES, H, ACQUIRER_HORIZON, FLOOR, SURPRISE_FLOOR, sorted(DIRECT), ALREADY_MOVED_SIGMA, POINTS,
                                     sorted(NEEDS_EXPECTATIONS)], sort_keys=True).encode()).hexdigest()[:12]


def horizon(event_type, asset_class, relation=None):
    if event_type not in H or asset_class not in CLASSES: return None
    if event_type == 'm&a' and asset_class == 'equity' and relation == 'acquirer': return ACQUIRER_HORIZON
    return H[event_type][CLASSES.index(asset_class)]


def _pct(actual, expected):
    try:
        a, e = float(actual), float(expected)
        return None if e == 0 else (a - e) / abs(e) * 100
    except (TypeError, ValueError):
        return None


def surprise_sign(ev):
    """(sign, big, conflict) from structured expectations; sign 0 = no usable surprise. Missing values stay missing."""
    x = ev.get('expectations') or {}; t = ev.get('event_type')
    if t == 'central-bank':
        a, e = x.get('rate_actual'), x.get('rate_expected')
        if a is None or e is None: return 0, False, False
        bp = (float(a) - float(e)) * 100
        return (0, False, False) if abs(bp) < SURPRISE_FLOOR['rate_bp'] else (1 if bp > 0 else -1, abs(bp) >= 2 * SURPRISE_FLOOR['rate_bp'], False)
    if t == 'macro-data':
        a, e = x.get('actual'), x.get('expected')
        s = _pct(a, e)
        if s is None or s == 0: return 0, False, False
        return (1 if s > 0 else -1) * (1 if x.get('higher_is') != 'negative' else -1), abs(s) >= 10, False
    signs, big = [], False
    for k, fl in (('eps', SURPRISE_FLOOR['eps']), ('revenue', SURPRISE_FLOOR['revenue']), ('guidance', SURPRISE_FLOOR['guidance'])):
        s = _pct(x.get(k + '_actual'), x.get(k + '_expected'))
        if s is not None and abs(s) >= fl: signs.append((k, 1 if s > 0 else -1)); big = big or abs(s) >= 2 * fl
    if not signs: return 0, False, False
    vals = {v for _, v in signs}
    if len(vals) == 1: return signs[0][1], big, False
    g = [v for k, v in signs if k == 'guidance']
    return (g[0], big, False) if g else (0, False, True)


def decide(ev, asset, ctx, threshold=None, calibrate=None, seen=()):
    """ev: extracted event (event_type, flags, expectations, catalysts); asset: {id, cls, relation, stance(+1/-1/0)};
    ctx: {pre_move_sigma: asset move from previous close to publication in sigma units (signed), ...}.
    Returns {decision: long|short|none, reasons, raw, confidence, horizon}."""
    t, cls, rel, flags = ev.get('event_type'), asset.get('cls'), asset.get('relation'), set(ev.get('flags') or [])
    out = {'decision': 'none', 'reasons': [], 'raw': 0, 'confidence': None, 'horizon': horizon(t, cls, rel)}
    r = out['reasons']
    for f in ('commentary', 'preview', 'price-move-recap', 'competing-catalysts'):
        if f in flags: r.append(f)
    if out['horizon'] is None: r.append('unsupported-combination')
    if rel not in DIRECT: r.append('indirect')
    key = (ev.get('event_id'), asset.get('id'), out['horizon'])
    if key in seen: r.append('duplicate-event')
    s, big, conflict = surprise_sign(ev)
    if conflict and 'competing-catalysts' not in r: r.append('competing-catalysts')
    stance = asset.get('stance') or 0
    if t in NEEDS_EXPECTATIONS:
        if s == 0 and not conflict: r.append('no-expectations')
        d = s * (asset.get('map') or 1)  # asset mapping for macro/rates (e.g. index = -1, currency = +1), set by the caller per §7
    else:
        d = stance
        if d == 0: r.append('stance-neutral')
    if d == 0 and t in NEEDS_EXPECTATIONS and 'no-expectations' not in r and 'competing-catalysts' not in r: r.append('stance-neutral')
    pre = ctx.get('pre_move_sigma')
    if d and pre is not None and pre * d >= ALREADY_MOVED_SIGMA: r.append('already-moved')
    raw = 0
    if t in NEEDS_EXPECTATIONS and s: raw += POINTS['expectations'] + (POINTS['big_surprise'] if big else 0)
    if rel in DIRECT: raw += POINTS['direct']
    if 'competing-catalysts' not in r: raw += POINTS['single_catalyst']
    if d and (pre is None or pre * d > -ALREADY_MOVED_SIGMA) and pre is not None: raw += POINTS['context_agrees']
    if d and stance and t in NEEDS_EXPECTATIONS and stance == s: raw += POINTS['stance_agrees']
    out['raw'] = raw
    if calibrate: out['confidence'] = calibrate(raw, t)
    if not r and threshold is not None and (out['confidence'] is None or out['confidence'] < threshold): r.append('below-threshold')
    if not r and d: out['decision'] = 'long' if d > 0 else 'short'
    return out


def meaningful(move_pct, cls, sigma_daily, horizon_days):
    """outcome-v4: the minimum move that counts as a hit or a miss."""
    return max(FLOOR.get(cls, .3), .5 * (sigma_daily or 0) * math.sqrt(max(horizon_days, .25)))
