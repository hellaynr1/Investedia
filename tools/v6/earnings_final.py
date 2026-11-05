"""Final holdout check for the validation-picked model (LightGBM, params frozen from validation):
(1) the validation-trained model on TEST, paired against always-short / always-long on the SAME calls (exact sign test);
(2) walk-forward: refit on TRAIN+VALIDATION (2022-2024) with the same params and thresholds-by-coverage, score TEST once.
  python3 -m tools.v6.earnings_final"""
import json, math, os
import numpy as np, lightgbm as lgb
from tools.v6.earnings_model import load, X, FEATS, DS, SEED, evaluate
def sign_p(b, c):
    n = b + c
    if not n: return 1.0
    k = min(b, c); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
def fit(rows, params):
    leaves, lr_, n = params; d = [r for r in rows if r['y']['res'] != 'flat']
    return lgb.LGBMClassifier(n_estimators=n, learning_rate=lr_, num_leaves=leaves, min_child_samples=200, subsample=.8, subsample_freq=1, colsample_bytree=.8,
                              reg_lambda=5.0, random_state=SEED, verbose=-1).fit(X(d), np.array([1 if r['y']['res'] == 'up' else 0 for r in d]))
def report(name, m, ref, test):
    pr, pt = m.predict_proba(X(ref))[:, 1], m.predict_proba(X(test))[:, 1]
    mg = sorted((abs(q - .5) for q in pr), reverse=True); out = {}
    for cov in (.10, .20, .30, .50, .75, 1.0):
        th = mg[int(cov * len(mg)) - 1] if cov < 1 else 0
        side = [(1 if q > .5 else -1) if abs(q - .5) >= th else 0 for q in pt]
        e = evaluate(test, side)
        sel = [(r, s) for r, s in zip(test, side) if s and r['y']['res'] != 'flat']
        mh = [(s > 0) == (r['y']['res'] == 'up') for r, s in sel]; sh = [r['y']['res'] == 'down' for r, s in sel]
        b = sum(1 for x, y in zip(mh, sh) if x and not y); c = sum(1 for x, y in zip(mh, sh) if y and not x)
        e['always_short_same_events'] = sum(sh) / len(sh) if sh else None; e['p_vs_always_short_paired'] = sign_p(b, c)
        e['longs'] = sum(1 for _, s in sel if s > 0); e['shorts'] = sum(1 for _, s in sel if s < 0)
        out[f'{int(cov * 100)}%'] = e
    return out
def main():
    rows = load(); S = {k: [r for r in rows if r['split'] == k] for k in ('train', 'val', 'test')}
    res = json.load(open(os.path.join(DS, 'results.json'))); params = tuple(res['models']['lightgbm']['params']['leaves,lr,n'])
    fin = {'params_from_validation': params,
           'A_trained_2022_23_thresholds_from_2024': report('A', fit(S['train'], params), S['val'], S['test']),
           'B_walk_forward_trained_2022_24_thresholds_from_2024_in_sample': report('B', fit(S['train'] + S['val'], params), S['val'], S['test'])}
    mB = fit(S['train'] + S['val'], params); mB.booster_.save_model(os.path.join(DS, 'model-v6e-shadow.txt'))
    pr = mB.predict_proba(X(S['val']))[:, 1]; mg = sorted((abs(q - .5) for q in pr), reverse=True)
    json.dump({'version': 'v6e-shadow-1', 'model': 'model-v6e-shadow.txt', 'features': FEATS, 'params': params, 'trained_on': '2022-01..2024-12 (entry_day)',
               'priority_margin_top10': mg[int(.10 * len(mg)) - 1], 'view_margin_top30': mg[int(.30 * len(mg)) - 1], 'status': 'SHADOW ONLY - no demonstrated edge over always-short on the 2025-26 holdout'},
              open(os.path.join(DS, 'model-v6e-shadow.json'), 'w'), indent=1)
    json.dump(fin, open(os.path.join(DS, 'final.json'), 'w'), indent=1, default=float)
    for k in ('A_trained_2022_23_thresholds_from_2024', 'B_walk_forward_trained_2022_24_thresholds_from_2024_in_sample'):
        print(k)
        for c, e in fin[k].items(): print(f"  {c:>4} n={e['decisive']:5d} acc={e['accuracy']*100:.1f}% [{e['ci95'][0]*100:.1f}-{e['ci95'][1]*100:.1f}] short-on-same={e['always_short_same_events']*100:.1f}% p={e['p_vs_always_short_paired']:.3f} L/S={e['longs']}/{e['shorts']} {e['mean_adj_ret_bp']:.0f}bp")
if __name__ == '__main__': main()
