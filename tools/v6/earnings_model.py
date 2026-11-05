"""v6 earnings-reaction models: baselines vs regularized logistic vs LightGBM, chronological splits, calibration, coverage curves.
Splits (fixed before any fitting, per ENGINE-V6-TRACK-D): TRAIN 2022-2023, VALIDATION 2024, TEST (untouched holdout) 2025-01-01..2026-10.
A 5-session embargo is applied at each split boundary. Every choice (features, hyperparameters, thresholds, model pick) is made on
VALIDATION only; TEST is scored once at the end. Confidence intervals: bootstrap over trading days (events on the same day move
together, so days, not events, are resampled).
  python3 -m tools.v6.earnings_model   -> research/v6/earnings-ds/results.json + REPORT.md + model files"""
import gzip, json, math, os, random, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DS = os.path.join(ROOT, 'research', 'v6', 'earnings-ds')
FEATS = ['surprise', 'surp_pos', 'abs_surprise', 'eps_pos', 'log_n_est', 'prev_surprise', 'has_prev', 'react_z', 'gap_z', 'move_z', 'mom5_z',
         'mom20', 'mom60', 'sigma20', 'log_dvol', 'vol_ratio_d', 'spy20', 'spy_sig', 'vix']
GROUPS = {'surprise': ['surprise', 'surp_pos', 'abs_surprise', 'eps_pos', 'log_n_est', 'prev_surprise', 'has_prev'], 'reaction': ['react_z', 'gap_z', 'move_z'],
          'momentum': ['mom5_z', 'mom20', 'mom60'], 'liquidity/vol': ['sigma20', 'log_dvol', 'vol_ratio_d'], 'regime': ['spy20', 'spy_sig', 'vix']}
COVS = [0.10, 0.20, 0.30, 0.50, 0.75, 1.00]
SEED = 7


def load():
    rows = [json.loads(l) for l in gzip.open(os.path.join(DS, 'dataset.jsonl.gz'), 'rt')]
    days = sorted({r['entry_day'] for r in rows})
    def split(d):
        if d < '2024-01-01': return 'train'
        if d < '2025-01-01': return 'val'
        return 'test'
    emb = set()
    for b in ('2024-01-01', '2025-01-01'):
        k = next(i for i, d in enumerate(days) if d >= b); emb |= set(days[max(0, k - 5):k])
    for r in rows: r['split'] = None if r['entry_day'] in emb else split(r['entry_day'])
    return [r for r in rows if r['split']]


def X(rows, feats=FEATS): return np.array([[r['f'][k] for k in feats] for r in rows], dtype=float)


def evaluate(rows, side, n_boot=400):
    """side: +1 long / -1 short / 0 no view, per row. Directional accuracy counts decisive (non-flat) outcomes only."""
    calls = [(r, s) for r, s in zip(rows, side) if s]
    dec = [(r, s) for r, s in calls if r['y']['res'] != 'flat']
    hits = [1 if (s > 0) == (r['y']['res'] == 'up') else 0 for r, s in dec]
    acc = sum(hits) / len(hits) if hits else None
    ret = [s * r['y']['adj'] for r, s in calls]
    byday = {}
    for (r, s), h in zip(dec, hits): byday.setdefault(r['entry_day'], []).append(h)
    ks = list(byday); rng = random.Random(SEED); bs = []
    for _ in range(n_boot if ks else 0):
        smp = [x for k in (rng.choice(ks) for _ in ks) for x in byday[k]]
        if smp: bs.append(sum(smp) / len(smp))
    bs.sort()
    ci = [bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1]] if bs else None
    return {'calls': len(calls), 'coverage': len(calls) / len(rows) if rows else 0, 'decisive': len(dec), 'flat': len(calls) - len(dec), 'hits': sum(hits),
            'accuracy': acc, 'ci95': ci, 'mean_adj_ret_bp': 1e4 * sum(ret) / len(ret) if ret else None}


def by_cov(rows, p, cuts):
    """cuts: list of (coverage, threshold on |p-0.5|) chosen on validation"""
    out = {}
    for cov, th in cuts:
        side = [(1 if q > .5 else -1) if abs(q - .5) >= th else 0 for q in p]
        out[f'{int(cov * 100)}%'] = evaluate(rows, side)
    return out


def thresholds(p_val, covs=COVS):
    m = sorted((abs(q - .5) for q in p_val), reverse=True)
    return [(c, m[max(0, min(len(m) - 1, int(c * len(m)) - 1))] if c < 1 else 0.0) for c in covs]


def brier(rows, p):
    d = [(q, 1 if r['y']['res'] == 'up' else 0) for r, q in zip(rows, p) if r['y']['res'] != 'flat']
    return sum((q - y) ** 2 for q, y in d) / len(d)


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.isotonic import IsotonicRegression
    import lightgbm as lgb
    rows = load()
    S = {k: [r for r in rows if r['split'] == k] for k in ('train', 'val', 'test')}
    dec = lambda rs: [r for r in rs if r['y']['res'] != 'flat']
    ytr = np.array([1 if r['y']['res'] == 'up' else 0 for r in dec(S['train'])])
    res = {'n': {k: len(v) for k, v in S.items()}, 'decisive': {k: len(dec(v)) for k, v in S.items()}, 'baselines': {}, 'models': {}}

    # ---- baselines (no fitting) ----
    base = {'always_long': lambda r: 1, 'always_short': lambda r: -1,
            'random_50_50': (lambda g: (lambda r: g.choice((1, -1))))(random.Random(SEED)),
            'surprise_sign': lambda r: r['f']['surp_pos'],
            'follow_reaction': lambda r: 1 if r['f']['move_z'] > 0 else -1,
            'fade_reaction': lambda r: -1 if r['f']['move_z'] > 0 else 1,
            'sector_market_momentum': lambda r: 1 if r['f']['spy20'] > 0 else -1}
    for k, fn in base.items(): res['baselines'][k] = {s: evaluate(S[s], [fn(r) for r in S[s]]) for s in ('val', 'test')}

    # ---- logistic (L2, C picked on validation) ----
    sc = StandardScaler().fit(X(dec(S['train'])))
    best = None
    for C in (0.001, 0.01, 0.1, 1.0):
        m = LogisticRegression(C=C, max_iter=2000).fit(sc.transform(X(dec(S['train']))), ytr)
        pv = m.predict_proba(sc.transform(X(S['val'])))[:, 1]; b = brier(S['val'], pv)
        if best is None or b < best[0]: best = (b, C, m)
    _, C, lr = best
    # ---- LightGBM (small, regularized; rounds/leaves picked on validation) ----
    gbest = None
    for leaves, lr_, n in ((7, .03, 300), (15, .03, 300), (15, .02, 600), (31, .02, 400)):
        g = lgb.LGBMClassifier(n_estimators=n, learning_rate=lr_, num_leaves=leaves, min_child_samples=200, subsample=.8, subsample_freq=1,
                               colsample_bytree=.8, reg_lambda=5.0, random_state=SEED, verbose=-1).fit(X(dec(S['train'])), ytr)
        pv = g.predict_proba(X(S['val']))[:, 1]; b = brier(S['val'], pv)
        if gbest is None or b < gbest[0]: gbest = (b, (leaves, lr_, n), g)
    _, gparams, gb = gbest
    preds = {'logistic': lambda rs: lr.predict_proba(sc.transform(X(rs)))[:, 1], 'lightgbm': lambda rs: gb.predict_proba(X(rs))[:, 1]}
    preds['ensemble'] = lambda rs: (preds['logistic'](rs) + preds['lightgbm'](rs)) / 2
    for name, fn in preds.items():
        pv, pt = fn(S['val']), fn(S['test'])
        # isotonic calibration fitted on validation (decisive rows), applied to test
        vd = [(q, 1 if r['y']['res'] == 'up' else 0) for r, q in zip(S['val'], pv) if r['y']['res'] != 'flat']
        iso = IsotonicRegression(out_of_bounds='clip').fit([a for a, _ in vd], [b for _, b in vd])
        pvc, ptc = iso.predict(pv), iso.predict(pt)
        cuts = thresholds(pv)
        res['models'][name] = {'params': {'C': C} if name == 'logistic' else ({'leaves,lr,n': gparams} if name == 'lightgbm' else 'mean of both'),
                               'brier_val_raw': brier(S['val'], pv), 'brier_test_raw': brier(S['test'], pt), 'brier_test_calibrated': brier(S['test'], ptc),
                               'brier_test_coinflip': .25, 'val': by_cov(S['val'], pv, cuts), 'test': by_cov(S['test'], pt, cuts),
                               'thresholds': {f'{int(c * 100)}%': th for c, th in cuts}}
        if name == 'lightgbm': p_lgb = (pv, pt, cuts)
        if name == 'logistic': p_lr = (pv, pt, cuts)
    # model choice on VALIDATION only: best accuracy at 30% coverage
    pick = max(res['models'], key=lambda k: res['models'][k]['val']['30%']['accuracy'] or 0)
    res['picked_on_validation'] = pick
    # ---- ablation (validation only, logistic refits) ----
    abl = {}
    for gname, gf in GROUPS.items():
        keep = [f for f in FEATS if f not in gf]
        s2 = StandardScaler().fit(X(dec(S['train']), keep))
        m2 = LogisticRegression(C=C, max_iter=2000).fit(s2.transform(X(dec(S['train']), keep)), ytr)
        pv2 = m2.predict_proba(s2.transform(X(S['val'], keep)))[:, 1]
        abl['without ' + gname] = {'brier_val': brier(S['val'], pv2), 'acc_val_30%': by_cov(S['val'], pv2, thresholds(pv2))['30%']['accuracy']}
    abl['all features'] = {'brier_val': res['models']['logistic']['brier_val_raw'], 'acc_val_30%': res['models']['logistic']['val']['30%']['accuracy']}
    res['ablation_validation'] = abl
    res['logistic_coefficients'] = dict(zip(FEATS, [round(float(c), 4) for c in lr.coef_[0]]))
    res['lightgbm_importance'] = dict(sorted(zip(FEATS, [int(v) for v in gb.feature_importances_]), key=lambda x: -x[1]))
    # ---- slices on TEST for the picked model at 30% coverage ----
    pv, pt, cuts = {'logistic': p_lr, 'lightgbm': p_lgb}.get(pick, p_lgb)
    th = dict(cuts)[.30]
    side = [(1 if q > .5 else -1) if abs(q - .5) >= th else 0 for q in pt]
    sl = {}
    def add(key, r, s): sl.setdefault(key, ([], []))[0].append(r); sl[key][1].append(s)
    for r, s in zip(S['test'], side):
        add('surprise ' + ('beat' if r['f']['surp_pos'] > 0 else 'miss' if r['f']['surp_pos'] < 0 else 'inline'), r, s)
        add('regime ' + ('VIX>=20' if r['f']['vix'] >= 20 else 'VIX<20'), r, s)
        add('liquidity ' + ('top half' if r['f']['log_dvol'] >= 16.5 else 'bottom half'), r, s)
        add('year ' + r['entry_day'][:4], r, s)
        add('call ' + ('long' if s > 0 else 'short' if s < 0 else 'none'), r, s)
    res['test_slices_picked_30%'] = {k: evaluate(a, b, 200) for k, (a, b) in sorted(sl.items())}
    # ---- persist model (coefficients + scaler; LightGBM text) ----
    json.dump({'version': 'v6-earnings-lr-1', 'features': FEATS, 'mean': sc.mean_.tolist(), 'scale': sc.scale_.tolist(), 'coef': lr.coef_[0].tolist(),
               'intercept': float(lr.intercept_[0]), 'C': C, 'thresholds': res['models']['logistic']['thresholds'], 'trained_on': 'entry_day < 2024-01-01 (5-session embargo)'},
              open(os.path.join(DS, 'model-logistic.json'), 'w'), indent=1)
    gb.booster_.save_model(os.path.join(DS, 'model-lightgbm.txt'))
    json.dump(res, open(os.path.join(DS, 'results.json'), 'w'), indent=1, default=float)
    print(json.dumps({'n': res['n'], 'picked': pick, 'test_30': res['models'][pick]['test']['30%'], 'test_100': res['models'][pick]['test']['100%'],
                      'always_long_test': res['baselines']['always_long']['test'], 'follow_test': res['baselines']['follow_reaction']['test']}, indent=1, default=float))


if __name__ == '__main__': main()
