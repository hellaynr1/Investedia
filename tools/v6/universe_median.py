"""Cross-sectional benchmark: per session, the median open->next-open log return across all cached stocks with >= $5M average
daily dollar volume (point-in-time: the 20 sessions before). Removes the 'median stock lags the cap-weighted index' bias that
makes 'always short vs SPY' look like an edge.  -> research/v6/earnings-ds/universe-median.json"""
import glob, gzip, json, math, os, statistics
from tools.v6.earnings_dataset import V6, OUT
def main():
    by = {}
    for p in glob.glob(os.path.join(V6, 'prices', '*.json.gz')):
        n = os.path.basename(p)[:-8]
        if not n.isalpha() or n.startswith('_'): continue
        try: d = json.load(gzip.open(p))
        except Exception: continue
        if not d.get('split_adjusted', True) and d.get('splits'): continue
        r = [x for x in d['d'] if x[1] and x[4] and x[1] > 0]
        for i in range(21, len(r) - 1):
            dv = sum(r[k][4] * (r[k][5] or 0) for k in range(i - 20, i)) / 20
            if dv < 5e6: continue
            x = math.log(r[i + 1][1] / r[i][1])
            if abs(x) < 0.5: by.setdefault(r[i][0], []).append(x)
    med = {d: statistics.median(v) for d, v in by.items() if len(v) >= 200}
    json.dump(med, open(os.path.join(OUT, 'universe-median.json'), 'w'))
    print(len(med), 'sessions')
if __name__ == '__main__': main()
