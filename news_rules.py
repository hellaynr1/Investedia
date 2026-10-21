"""Offline editorial rules. Tags describe exposure, never a price forecast."""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def matches(pattern, text):
    return bool(re.search(pattern, text, re.I))

# A topic alone is not a major event: require a decision, release or disruption.
RULES = [
    ('rates', 'economy', r'\b(fed|federal reserve|ecb|bank of england|central bank|interest rates?)\b', r'\b(rate (?:hike|cut|decision)|raises?|cuts?|holds?|decision|basis points)\b'),
    ('economy', 'economy', r'\b(cpi|inflation|payrolls|unemployment|jobs report|gdp)\b', r'\b(report|data|rises?|falls?|slows?|accelerates?|unexpected|surges?|drops?|release)\b'),
    ('earnings', 'companies', r'\b(earnings|revenue|profit|guidance)\b', r'\b(beats?|miss(?:es)?|cuts?|raises?|warns?|record|slumps?|surges?)\b'),
    ('politics', 'geopolitics', r'\b(election|elections|government|president|parliament|congress|budget|tax|taxes|regulation|regulator|tariffs?|sanctions?|export ban|trade deal|war|conflict|ceasefire)\b', r'\b(wins?|results?|approves?|passes?|imposes?|announces?|signs?|bans?|cuts?|raises?|collapses?|tariffs?|sanctions?|export ban|trade deal|war|ceasefire)\b'),
    ('supply', 'commodities', r'\b(oil|opec|gas|shipping|supply|port|pipeline|strait|red sea)\b', r'\b(cuts?|disruption|disrupts?|blockade|closes?|halts?|shortage|attack|shutdown)\b'),
    ('markets', 'markets', r'\b(stocks?|shares?|bonds?|markets?|bitcoin|crypto|gold|crude)\b', r'\b(crash(?:es)?|plunges?|surges?|sell.off|record high|circuit breaker)\b'),
]
FINANCIAL = r'\b(fed|federal reserve|ecb|bank of england|interest rates?|rate cut|rate hike|stock|stocks|shares|bond|bonds|market|markets|economy|economic|inflation|bank|earnings|revenue|profit|guidance|merger|acquisition|bankruptcy|ipo|oil|opec|gas|gold|copper|wheat|bitcoin|crypto|semiconductor|tariff|tariffs|sanctions|export ban|trade deal|budget|tax|taxes|regulation|trade|supply|shipping|energy)\b'
NOISE = r'\b(stock to buy|stocks to buy|price target|horoscope|celebrity|football|soccer)\b'


def classify(title, description='', official=False):
    text = title + ' ' + description
    hits = [key for key, _, topic, event in RULES if matches(topic, text) and matches(event, title)]
    if matches(NOISE, title): return None
    # Elections/conflicts need an economic connection too; politics is covered neutrally.
    if not matches(FINANCIAL, text): return None
    category = next((cat for key, cat, _, _ in RULES if key in hits), 'companies')
    if 'politics' in hits: category = 'geopolitics'
    if not hits:
        if matches(r'\b(bitcoin|crypto)\b', text): category = 'crypto'
        elif matches(r'\b(semiconductor|artificial intelligence|technology)\b', text): category = 'technology'
    # Smaller company earnings remain headline-only unless a large tracked company is involved.
    major = bool(set(hits) - {'earnings'}) or ('earnings' in hits and any(e.get('major') for e in entities_for(title)))
    return {'category': category, 'importance': 3 if major else 1, 'priority_topics': hits, 'summary_priority': major}


@lru_cache(maxsize=1)
def company_reference():
    rows = json.loads((ROOT / 'assets/globe/markets.json').read_text())['assets']
    out = []
    for a in rows:
        if a.get('t') != 'stocks' or a.get('g') == 'Index': continue
        out.append(a)
    # Some market datasets call individual equities 'stock'.
    if not out:
        out = [a for a in rows if a.get('t') in ('stock', 'equity')]
    return out


def entities_for(title):
    found = []
    for a in company_reference():
        name = a['n']
        short = re.sub(r'\s+(Inc\.?|Corporation|Corp\.?|plc|Ltd\.?)$', '', name, flags=re.I)
        ticker = a['s']
        if (len(short) >= 4 and matches(r'(?<!\w)' + re.escape(short) + r'(?!\w)', title)) or re.search(r'\$' + re.escape(ticker) + r'\b', title):
            found.append({'name': name, 'ticker': ticker, 'sym': a.get('site'), 'major': ticker in {'AAPL','MSFT','NVDA','AMZN','GOOGL','META','TSLA','TSM','JPM','XOM'}, '_country': a.get('k')})
    return found[:4]


# Global sectors have no invented home country. Direction stays unclear.
EXPOSURES = [
    (r'\b(oil|opec|crude|refinery)\b', [('Crude oil', 'BZ=F', 'Supply and demand changes can affect oil prices.'), ('Energy companies', None, 'Oil prices affect producers’ revenues and costs.'), ('Airlines', None, 'Fuel prices affect airlines’ operating costs.')]),
    (r'\b(shipping|port|red sea|strait|freight)\b', [('Shipping companies', None, 'Route availability and freight costs affect shipping operations.'), ('Importers and exporters', None, 'Transport disruption can change delivery times and costs.')]),
    (r'\b(fed|federal reserve)\b', [('US Treasuries', '^TNX', 'US rate expectations affect Treasury yields and bond prices.'), ('US dollar', 'DX-Y.NYB', 'Relative interest rates can affect demand for the dollar.'), ('US equities', '^GSPC', 'Interest rates affect financing costs and valuations.'), ('Gold', 'GC=F', 'Interest rate expectations can affect demand for gold.')]),
    (r'\b(ecb|european central bank)\b', [('Euro', 'EURUSD=X', 'Euro area interest rates can affect the euro.'), ('Euro area bonds', None, 'Rate expectations affect bond yields and prices.')]),
    (r'\b(bank of england)\b', [('British pound', 'GBPUSD=X', 'UK interest rates can affect the pound.'), ('UK government bonds', None, 'UK rate expectations affect gilt yields and prices.')]),
    (r'\b(cpi|inflation|payrolls|unemployment|jobs report|gdp)\b', [('Government bonds', None, 'Economic releases can change interest rate expectations.'), ('Equities', None, 'Growth and inflation affect earnings expectations and valuations.'), ('Currencies', None, 'Economic releases can change relative interest rate expectations.')]),
    (r'\b(tariffs?|export ban|trade deal|sanctions?)\b', [('Importers and exporters', None, 'Trade restrictions and agreements can change market access and costs.'), ('Manufacturers', None, 'Trade policy can affect input costs and supply chains.')]),
    (r'\b(election|elections|budget|tax|taxes|government|parliament|congress|regulation|regulator)\b', [('Domestic equities', None, 'Policy changes may affect businesses in the country concerned.'), ('Government bonds', None, 'Budget and policy changes may affect borrowing expectations.'), ('Local currency', None, 'Policy uncertainty may affect the currency of the country concerned.')]),
    (r'\b(war|conflict|ceasefire|military)\b', [('Energy markets', None, 'Conflict can disrupt energy production and transport.'), ('Gold', 'GC=F', 'Geopolitical uncertainty can change demand for gold.'), ('Transport companies', None, 'Conflict can affect routes, insurance and operating costs.')]),
    (r'\b(semiconductor|chip|chips)\b', [('Semiconductor companies', None, 'Chip supply and demand affect semiconductor businesses.')]),
    (r'\b(bitcoin|crypto)\b', [('Bitcoin', 'BTC-USD', 'Crypto developments may affect demand and market access.')]),
]


def rule_impacts(title, entities=()):
    rows = []
    for e in entities:
        rows.append({'kind': 'company', 'name': e['name'], 'ticker': e.get('ticker'), 'country': None, 'direction': 'unclear', 'why': 'This company is directly mentioned in the reporting.'})
    for pattern, targets in EXPOSURES:
        if matches(pattern, title):
            rows.extend({'kind': 'asset' if ticker else 'sector', 'name': name, 'ticker': ticker, 'country': None, 'direction': 'unclear', 'why': why} for name, ticker, why in targets)
    unique = {row['name']: row for row in rows}
    return list(unique.values())[:6]
