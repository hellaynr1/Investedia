"""Fetch attributed homepage snapshots. No credentials; no fabricated fallback data.

Run before build.py. Each feed retains its own timestamp on failure.
"""
import datetime as dt
import json
import pathlib
import shutil
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent
PATH = ROOT / 'assets/home-data.js'
NOW = dt.datetime.now(dt.timezone.utc)


def get(url, origin='https://www.tradingview.com'):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Origin': origin, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def crypto():
    d = get('https://api.coingecko.com/api/v3/global')['data']
    return {'source': 'CoinGecko', 'url': 'https://www.coingecko.com/en/global-charts',
            'asof': dt.datetime.fromtimestamp(d['updated_at'], dt.timezone.utc).isoformat(),
            'cap': d['total_market_cap']['usd'], 'volume': d['total_volume']['usd'],
            'change': d['market_cap_change_percentage_24h_usd'],
            'btc': d['market_cap_percentage']['btc'], 'eth': d['market_cap_percentage']['eth']}


def coins():
    ids = 'bitcoin,ethereum,solana,ripple,binancecoin,dogecoin,cardano,avalanche-2,chainlink,uniswap,aave,tether,usd-coin'
    rows = get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=' + ids)
    return {'source': 'CoinGecko', 'url': 'https://www.coingecko.com/', 'items': {r['symbol'].upper():
            {'cap':r['market_cap'],'rank':r['market_cap_rank'],'ath':r['ath'],'circulating':r['circulating_supply'],
             'asof':r['last_updated']} for r in rows}}


def fear():
    d = get('https://api.alternative.me/fng/?limit=1')['data'][0]
    return {'source': 'Alternative.me', 'url': 'https://alternative.me/crypto/fear-and-greed-index/',
            'asof': dt.datetime.fromtimestamp(int(d['timestamp']), dt.timezone.utc).isoformat(),
            'value': int(d['value']), 'label': d['value_classification']}


SECTORS = {'XLV': 'Healthcare', 'XLU': 'Utilities', 'XLF': 'Financials', 'XLI': 'Industrials',
           'XLC': 'Communication', 'XLB': 'Materials', 'XLY': 'Consumer discretionary',
           'XLP': 'Consumer staples', 'XLK': 'Technology', 'XLE': 'Energy', 'XLRE': 'Real estate'}


def sector(pair):
    sym, name = pair
    d = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5d&interval=1d')['chart']['result'][0]
    closes = [v for v in d['indicators']['quote'][0]['close'] if v is not None]
    if len(closes) < 2:
        raise ValueError('Insufficient sector history')
    return {'symbol': sym, 'name': name, 'change': (d['meta']['regularMarketPrice'] / closes[-2] - 1) * 100,
            'asof': dt.datetime.fromtimestamp(d['meta']['regularMarketTime'], dt.timezone.utc).isoformat()}


def sectors():
    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(sector, SECTORS.items()))
    return {'source': 'Yahoo Finance · Select Sector SPDR ETFs (proxies)',
            'url': 'https://www.sectorspdrs.com/', 'asof': min(r['asof'] for r in rows), 'items': rows}


def active():
    url = 'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=most_actives&count=250'
    rows = get(url)['finance']['result'][0]['quotes']
    return {'source': 'Yahoo Finance', 'url': 'https://finance.yahoo.com/markets/stocks/most-active/',
            'items': {r['symbol']: {'volume': r.get('regularMarketVolume'), 'cap': r.get('marketCap'),
                                  'pe': r.get('trailingPE')} for r in rows}}


def calendar():
    start = NOW.strftime('%Y-%m-%dT00:00:00.000Z')
    end = (NOW + dt.timedelta(days=8)).strftime('%Y-%m-%dT23:59:59.000Z')
    url = 'https://economic-calendar.tradingview.com/events?' + urllib.parse.urlencode({'from': start, 'to': end}) + '&countries=US,EU,GB,CN'
    rows = get(url)['result']
    return {'source': 'TradingView', 'url': 'https://www.tradingview.com/economic-calendar/', 'items': rows}


def earnings():
    rows = []
    for offset in range(8):
        day = (NOW + dt.timedelta(days=offset)).date()
        if day.weekday() >= 5:
            continue
        d = get(f'https://api.nasdaq.com/api/calendar/earnings?date={day}', 'https://www.nasdaq.com')
        for r in (d.get('data') or {}).get('rows') or []:
            rows.append(dict(r, date=str(day)))
        if len(rows) >= 30:
            break
    return {'source': 'Nasdaq · expected reporting dates', 'url': 'https://www.nasdaq.com/market-activity/earnings', 'items': rows}


def main():
    old = json.loads(PATH.read_text().removeprefix('window.HOME_DATA=').strip().removesuffix(';')) if PATH.exists() else {}
    def run(pair):
        key, fn = pair
        try:
            result = fn()
            result['fetched'] = NOW.isoformat()
            result.setdefault('asof', NOW.isoformat())
            return key, result, None
        except Exception as error:
            return key, None, str(error)
    with ThreadPoolExecutor(6) as pool:
        for key, result, error in pool.map(run, {'crypto': crypto, 'coins': coins, 'fear': fear, 'sectors': sectors,
                                               'active': active, 'calendar': calendar, 'earnings': earnings}.items()):
            if result is not None:
                old[key] = result
            print(f'{key}: {error or "updated"}', flush=True)
    PATH.write_text('window.HOME_DATA=' + json.dumps(old, separators=(',', ':')).replace('<', '\\u003c') + ';\n')
    if (ROOT / 'docs/assets').is_dir():
        shutil.copy2(PATH, ROOT / 'docs/assets/home-data.js')


if __name__ == '__main__':
    main()
