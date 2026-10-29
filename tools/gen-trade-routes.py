"""Writes assets/globe/trade.json: the biggest export routes between major economies, from UN Comtrade (public preview API, no key).
Each route: exporter ISO2 -> partner ISO2, value in US dollars, year. Only real reported totals (HS TOTAL); no estimates.
Run once a year: python3 tools/gen-trade-routes.py"""
import json, time, urllib.request
YEAR, TOP = 2023, 5
REPORTERS = [842, 156, 276, 392, 826, 251, 699, 410, 528, 124, 484, 76, 36, 682, 380, 702, 757, 724, 56, 710, 566, 818, 764, 360, 784,
             792, 616, 752, 578, 704, 458, 608, 32, 152, 170, 604, 376, 634, 398, 586, 50, 404, 504, 288, 231, 24, 12, 554, 372, 40, 208, 246, 203, 620, 300, 348, 642, 368, 414, 344, 384, 834, 218, 643, 862]  # + Turkey, Poland, Sweden, Norway, Vietnam, Malaysia, Philippines, Argentina, Chile, Colombia, Peru, Israel, Qatar, Kazakhstan, Pakistan, Bangladesh, Kenya, Morocco, Ghana, Ethiopia, Angola, Algeria, New Zealand, Ireland, Austria, Denmark, Finland, Czechia, Portugal, Greece, Hungary, Romania, Iraq, Kuwait, Hong Kong, Côte d'Ivoire, Tanzania, Ecuador, Russia, Venezuela  # US, China, Germany, Japan, UK, France, India, S.Korea, Netherlands, Canada, Mexico, Brazil, Australia, Saudi, Italy, Singapore, Switzerland, Spain, Belgium, South Africa, Nigeria, Egypt, Thailand, Indonesia, UAE
UA = {'User-Agent': 'Investedia/1.0 (+https://investedia.com)'}
get = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read())
ref = get('https://comtradeapi.un.org/files/v1/app/reference/partnerAreas.json')
areas = {r['PartnerCode']: r for r in ref.get('results', ref)}
iso = lambda c: (areas.get(c) or {}).get('PartnerCodeIsoAlpha2') if not (areas.get(c) or {}).get('isGroup') else None
routes = {}
for rc in REPORTERS:
    try:
        rows = get(f'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode={rc}&period={YEAR}&flowCode=X&cmdCode=TOTAL')['data']
    except Exception as e:
        print('skip', rc, e); time.sleep(2); continue
    src = iso(rc); best = sorted([r for r in rows if iso(r['partnerCode']) and r['partnerCode'] != rc], key=lambda r: -(r['primaryValue'] or 0))[:TOP]
    for r in best:
        dst = iso(r['partnerCode']); key = tuple(sorted((src, dst)))
        if key not in routes or routes[key]['usd'] < r['primaryValue']:
            routes[key] = {'from': src, 'to': dst, 'usd': round(r['primaryValue']), 'year': YEAR}
    print(src, [(iso(r['partnerCode']), round(r['primaryValue'] / 1e9)) for r in best]); time.sleep(1.3)
out = {'source': 'UN Comtrade (public data), exports, HS total', 'year': YEAR, 'routes': sorted(routes.values(), key=lambda r: -r['usd'])}
for d in ('assets/globe', 'docs/assets/globe'): json.dump(out, open(d + '/trade.json', 'w'), separators=(',', ':'))
print(len(out['routes']), 'routes')
