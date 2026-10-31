"""Forward evaluation report for Prediction Engine v4 (research/ENGINE-V4.md §11). Works on the shadow ledger (evidence) or on the
development replay (NOT evidence). Coverage is first-class; accuracy only from judged outcomes; Priority Insights are reported as a
subset of Market Views, never as extra independent predictions.  python3 tools/eval/forward_report.py research/v4-replay.json"""
import json, sys, collections

GARBAGE = {'commentary', 'preview', 'price-move-recap', 'unsupported-combination', 'unresolved-asset', 'indirect'}
VIEW = ('standard', 'priority')


def independent(views):
    """Correlated-view collapse (same asset + direction, overlapping horizon windows): how many views are independent evidence."""
    keep, last = 0, {}
    for r in sorted(views, key=lambda r: r.get('start_ts') or 0):
        k = (r.get('asset_id'), r.get('decision')); t = r.get('start_ts') or 0
        if k in last and t < last[k]: continue
        keep += 1; last[k] = t + {'6h': .25, 'S1': 1.5, '24h': 1, 'S2': 3, '48h': 2}.get(r.get('horizon'), 1) * 86400
    return keep


def coverage(recs):
    ev = collections.defaultdict(list)
    for r in recs: ev[r.get('event_id') or r['article_id']].append(r)
    eligible = {e for e, rs in ev.items() if any(r.get('asset_id') and r.get('horizon') and not (set(r.get('reasons') or []) & GARBAGE) for r in rs)}
    views = [r for r in recs if r.get('view_tier') in VIEW]; pri = [r for r in views if r['view_tier'] == 'priority']
    days = {r['start'][:10] for r in recs} or {''}
    covered = {r.get('event_id') or r['article_id'] for r in views}
    no_view = collections.Counter(x for r in recs if r.get('view_tier') == 'none' for x in (r.get('tier_reasons') or r.get('reasons') or ['?']))
    std_why = collections.Counter(g for r in views if r['view_tier'] == 'standard' for g in r.get('tier_reasons') or [])
    gates = {g: dict(collections.Counter((r.get('gates') or {}).get(g) for r in views)) for g in sorted({g for r in views for g in (r.get('gates') or {})})}
    return {'events_analysed': len(ev), 'eligible_events': len(eligible), 'asset_records': len(recs), 'market_views': len(views), 'of_which_priority_insights': len(pri),
            'no_view_records': len(recs) - len(views), 'eligible_events_with_a_view': len(covered & eligible),
            'coverage_pct': round(100 * len(covered & eligible) / max(1, len(eligible)), 1), 'independent_views': independent(views),
            'days': len(days), 'views_per_day': round(len(views) / len(days), 1), 'priority_per_day': round(len(pri) / len(days), 1),
            'priority_share_of_views_pct': round(100 * len(pri) / max(1, len(views)), 1),
            'no_view_reasons': dict(no_view.most_common()), 'standard_because_gate_failed': dict(std_why.most_common()), 'gate_results_on_views': gates,
            'views_by_event_type': dict(collections.Counter(r['event_type'] for r in views).most_common()),
            'views_by_class': dict(collections.Counter(r.get('cls') for r in views).most_common()),
            'views_with_expectations': sum(1 for r in views if r.get('expectations_available'))}


def accuracy(views):
    j = [r for r in views if (r.get('outcome') or {}).get('res') in ('hit', 'miss')]
    h = sum(r['outcome']['res'] == 'hit' for r in j)
    return {'judged': len(j), 'hits': h, 'accuracy_pct': round(100 * h / len(j), 1) if j else None}


def curve(views):
    """Quality/coverage curve: for each raw-score level, views kept, their share and accuracy (thresholds are chosen on VALIDATION only)."""
    out = []
    for k in sorted({r.get('raw_score', 0) for r in views}):
        keep = [r for r in views if r.get('raw_score', 0) >= k]
        out.append({'min_raw_score': k, 'views': len(keep), 'share_of_views_pct': round(100 * len(keep) / max(1, len(views)), 1), **accuracy(keep)})
    return out


def report(d, source=''):
    recs = d.get('records') or []
    views = [r for r in recs if r.get('view_tier') in VIEW]
    return {'source': source, 'note': d.get('note'), 'coverage': coverage(recs), 'market_views': accuracy(views),
            'priority_insights_subset': accuracy([r for r in views if r['view_tier'] == 'priority']),
            'standard_views_only': accuracy([r for r in views if r['view_tier'] == 'standard']), 'quality_coverage_curve': curve(views)}


if __name__ == '__main__':
    print(json.dumps(report(json.load(open(sys.argv[1])), sys.argv[1]), indent=1))
