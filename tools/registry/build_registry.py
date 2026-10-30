"""Builds data/registry.json, the canonical asset/entity registry (see registry.py for ids and rules).

  python3 tools/registry/build_registry.py [--history stories.json]

Inputs: fixed tables below (indices, currencies, crypto, commodities, rates), assets/globe/markets.json (places already shown on the
Globe), the site's own symbols (update_market.YAHOO, assets/mock.js), every ticker the news has used (news-live, news-archive and the
event archive, plus --history), the SEC company-ticker file (all US-listed issuers) and Yahoo Finance security records for
exchange-qualified symbols. Nothing is guessed: a symbol that no official record confirms is left out, and a Globe asset whose
display name does not match its official owner is reported as a conflict instead of being kept."""
import json, os, re, sys, glob, argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import registry as R
import sources as S
from update_market import YAHOO, FRED

NY = (40.707, -74.011)
# Yahoo exchange code -> (MIC, city, lat, lon, ISO2). Equity listings without a better place sit at their exchange ("listing-venue").
VENUES = {
    'NYQ': ('XNYS', 'New York', *NY, 'US'), 'NMS': ('XNAS', 'New York', *NY, 'US'), 'NGM': ('XNAS', 'New York', *NY, 'US'), 'NCM': ('XNAS', 'New York', *NY, 'US'),
    'NIM': ('XNAS', 'New York', *NY, 'US'), 'PCX': ('ARCX', 'New York', *NY, 'US'), 'ASE': ('XASE', 'New York', *NY, 'US'), 'BTS': ('BATS', 'Chicago', 41.878, -87.63, 'US'),
    'PNK': ('OTCM', 'New York', *NY, 'US'), 'OQX': ('OTCM', 'New York', *NY, 'US'), 'OQB': ('OTCM', 'New York', *NY, 'US'),
    'LSE': ('XLON', 'London', 51.515, -0.099, 'GB'), 'PAR': ('XPAR', 'Paris', 48.869, 2.341, 'FR'), 'GER': ('XETR', 'Frankfurt', 50.11, 8.68, 'DE'),
    'FRA': ('XFRA', 'Frankfurt', 50.11, 8.68, 'DE'), 'JPX': ('XTKS', 'Tokyo', 35.68, 139.77, 'JP'), 'OSA': ('XOSE', 'Osaka', 34.69, 135.50, 'JP'),
    'HKG': ('XHKG', 'Hong Kong', 22.283, 114.158, 'HK'), 'NSI': ('XNSE', 'Mumbai', 19.06, 72.86, 'IN'), 'BSE': ('XBOM', 'Mumbai', 18.93, 72.83, 'IN'),
    'ASX': ('XASX', 'Sydney', -33.868, 151.209, 'AU'), 'SAO': ('BVMF', 'São Paulo', -23.548, -46.636, 'BR'), 'STO': ('XSTO', 'Stockholm', 59.333, 18.065, 'SE'),
    'SES': ('XSES', 'Singapore', 1.283, 103.851, 'SG'), 'EBS': ('XSWX', 'Zurich', 47.377, 8.54, 'CH'), 'JNB': ('XJSE', 'Johannesburg', -26.106, 28.054, 'ZA'),
    'KSC': ('XKRX', 'Seoul', 37.522, 126.927, 'KR'), 'KOE': ('XKOS', 'Seoul', 37.522, 126.927, 'KR'), 'MIL': ('XMIL', 'Milan', 45.464, 9.19, 'IT'),
    'TOR': ('XTSE', 'Toronto', 43.648, -79.381, 'CA'), 'VAN': ('XTSX', 'Toronto', 43.648, -79.381, 'CA'), 'MEX': ('XMEX', 'Mexico City', 19.433, -99.133, 'MX'),
    'HEL': ('XHEL', 'Helsinki', 60.17, 24.938, 'FI'), 'MCE': ('XMAD', 'Madrid', 40.417, -3.704, 'ES'), 'AMS': ('XAMS', 'Amsterdam', 52.374, 4.89, 'NL'),
    'IST': ('XIST', 'Istanbul', 41.015, 28.979, 'TR'), 'TAI': ('XTAI', 'Taipei', 25.033, 121.565, 'TW'), 'TWO': ('ROCO', 'Taipei', 25.033, 121.565, 'TW'),
    'OSL': ('XOSL', 'Oslo', 59.913, 10.752, 'NO'), 'SHH': ('XSHG', 'Shanghai', 31.23, 121.474, 'CN'), 'SHZ': ('XSHE', 'Shenzhen', 22.543, 114.058, 'CN'),
    'KLS': ('XKLS', 'Kuala Lumpur', 3.139, 101.687, 'MY'), 'SAU': ('XSAU', 'Riyadh', 24.713, 46.675, 'SA'), 'TLV': ('XTAE', 'Tel Aviv', 32.085, 34.782, 'IL'),
    'CPH': ('XCSE', 'Copenhagen', 55.676, 12.568, 'DK'), 'BRU': ('XBRU', 'Brussels', 50.85, 4.352, 'BE'), 'NZE': ('XNZE', 'Wellington', -41.287, 174.776, 'NZ'),
    'WSE': ('XWAR', 'Warsaw', 52.23, 21.011, 'PL'), 'JKT': ('XIDX', 'Jakarta', -6.209, 106.846, 'ID'), 'SET': ('XBKK', 'Bangkok', 13.756, 100.502, 'TH'),
    'BUE': ('XBUE', 'Buenos Aires', -34.604, -58.382, 'AR'), 'VIE': ('XWBO', 'Vienna', 48.208, 16.372, 'AT'), 'LIS': ('XLIS', 'Lisbon', 38.722, -9.139, 'PT'),
    'SGO': ('XSGO', 'Santiago', -33.449, -70.669, 'CL'), 'ISE': ('XDUB', 'Dublin', 53.349, -6.26, 'IE'), 'CAI': ('XCAI', 'Cairo', 30.044, 31.236, 'EG'),
    'ATH': ('XATH', 'Athens', 37.984, 23.728, 'GR'), 'VSE': ('XSTC', 'Ho Chi Minh City', 10.776, 106.701, 'VN'), 'PRA': ('XPRA', 'Prague', 50.088, 14.42, 'CZ'),
    'BUD': ('XBUD', 'Budapest', 47.498, 19.04, 'HU'), 'DFM': ('XDFM', 'Dubai', 25.205, 55.271, 'AE'), 'DOH': ('DSMD', 'Doha', 25.286, 51.531, 'QA'),
    'KUW': ('XKUW', 'Kuwait City', 29.376, 47.977, 'KW'), 'BVC': ('XBOG', 'Bogotá', 4.711, -74.072, 'CO'), 'LIM': ('XLIM', 'Lima', -12.046, -77.043, 'PE'),
}
SEC_MIC = {'NYSE': 'XNYS', 'Nasdaq': 'XNAS', 'CBOE': 'BATS', 'OTC': 'OTCM', 'TXSE': 'XTXS'}

# ---------- fixed tables (non-equity assets) ----------
# Indices: id code -> (Yahoo price symbol, name, city, lat, lon, name patterns). Places follow the Globe's own index places where it has one.
INDICES = {
    'SPX': ('^GSPC', 'S&P 500', [r's ?& ?p ?500( index)?', r'standard (and|&) poor.?s 500']), 'NDX': ('^NDX', 'Nasdaq 100', [r'nasdaq[- ]100( index)?']),
    'IXIC': ('^IXIC', 'Nasdaq Composite', [r'nasdaq composite( index)?']), 'DJI': ('^DJI', 'Dow Jones Industrial Average', [r'(the )?dow( jones)?( industrial average| industrials| 30)?']),
    'RUT': ('^RUT', 'Russell 2000', [r'russell 2000( index)?']), 'VIX': ('^VIX', 'Cboe Volatility Index', [r'(cboe )?(vix|volatility index)']),
    'TSX': ('^GSPTSE', 'S&P/TSX Composite', [r's ?& ?p ?/ ?tsx( composite)?( index)?', r'tsx( composite)?( index)?']),
    'MXX': ('^MXX', 'S&P/BMV IPC', [r's ?& ?p ?/ ?bmv ipc', r'(mexico.?s )?ipc( index)?']), 'IBOV': ('^BVSP', 'Ibovespa', [r'i?bovespa( index)?']),
    'MERV': ('^MERV', 'S&P Merval', [r'(s ?& ?p )?merval( index)?']), 'UKX': ('^FTSE', 'FTSE 100', [r'ftse 100( index)?']),
    'DAX': ('^GDAXI', 'DAX', [r'(german )?dax( 40)?( index)?']), 'CAC': ('^FCHI', 'CAC 40', [r'cac 40( index)?']),
    'SX5E': ('^STOXX50E', 'Euro Stoxx 50', [r'euro ?stoxx 50( index)?']), 'STOXX600': ('^STOXX', 'Stoxx Europe 600', [r'(stoxx|stoxx europe) 600( index)?', r'pan.european stoxx 600']),
    'SMI': ('^SSMI', 'Swiss Market Index', [r'swiss market index', r'smi']), 'AEX': ('^AEX', 'AEX', [r'aex( index)?']), 'IBEX': ('^IBEX', 'IBEX 35', [r'ibex( 35)?( index)?']),
    'FTSEMIB': ('FTSEMIB.MI', 'FTSE MIB', [r'ftse mib( index)?']), 'NKY': ('^N225', 'Nikkei 225', [r'nikkei( 225)?( stock average| index)?']),
    'TOPIX': ('^TOPX', 'TOPIX', [r'topix( index)?']), 'SSEC': ('000001.SS', 'Shanghai Composite', [r'shanghai composite( index)?']),
    'SZSE': ('399001.SZ', 'Shenzhen Component', [r'shenzhen component( index)?']), 'HSI': ('^HSI', 'Hang Seng', [r'hang seng( index)?']),
    'NIFTY': ('^NSEI', 'Nifty 50', [r'(nse )?nifty( 50)?( index)?']), 'SENSEX': ('^BSESN', 'BSE Sensex', [r'(bse |s ?& ?p bse )?sensex( index)?']),
    'KOSPI': ('^KS11', 'KOSPI', [r'kospi( index| composite)?']), 'TWII': ('^TWII', 'Taiwan Weighted', [r'taiex', r'taiwan weighted( index)?']),
    'STI': ('^STI', 'Straits Times Index', [r'straits times index', r'sti']), 'JKSE': ('^JKSE', 'Jakarta Composite', [r'jakarta composite( index)?']),
    'KLSE': ('^KLSE', 'FTSE Bursa Malaysia KLCI', [r'(ftse bursa malaysia )?klci']), 'TA125': ('^TA125.TA', 'TA-125', [r'ta.?125( index)?']),
    'J203': ('^J203.JO', 'JSE All Share', [r'jse all.share( index)?']), 'XJO': ('^AXJO', 'S&P/ASX 200', [r'(s ?& ?p ?/ ?)?asx ?200( index)?']),
    'NZ50': ('^NZ50', 'NZX 50', [r'nzx ?50( index)?']), 'BIST100': ('XU100.IS', 'BIST 100', [r'bist ?100( index)?', r'borsa istanbul 100']),
    'TASI': ('^TASI.SR', 'Tadawul All Share', [r'tadawul( all share)?( index)?', r'tasi']), 'OMXS30': ('^OMX', 'OMX Stockholm 30', [r'omx stockholm 30', r'omxs30']),
    'EGX30': ('^EGX30.CA', 'EGX 30', [r'egx ?30( index)?']),
}
SITE_INDEX = {'ES1': ('ES=F', 'S&P 500 futures'), 'YM1': ('YM=F', 'Dow futures'), 'NQ1': ('NQ=F', 'Nasdaq 100 futures')}
CITY = {'US': ('New York', *NY), 'CA': ('Toronto', 43.648, -79.381), 'MX': ('Mexico City', 19.433, -99.133), 'BR': ('São Paulo', -23.548, -46.636),
        'AR': ('Buenos Aires', -34.604, -58.382), 'GB': ('London', 51.515, -0.099), 'DE': ('Frankfurt', 50.11, 8.68), 'FR': ('Paris', 48.869, 2.341),
        'EU': ('Frankfurt', 50.11, 8.68), 'CH': ('Zurich', 47.377, 8.54), 'NL': ('Amsterdam', 52.374, 4.89), 'ES': ('Madrid', 40.417, -3.704),
        'IT': ('Milan', 45.464, 9.19), 'JP': ('Tokyo', 35.68, 139.77), 'CN': ('Shanghai', 31.23, 121.474), 'HK': ('Hong Kong', 22.283, 114.158),
        'IN': ('Mumbai', 19.06, 72.86), 'KR': ('Seoul', 37.522, 126.927), 'TW': ('Taipei', 25.033, 121.565), 'SG': ('Singapore', 1.283, 103.851),
        'ID': ('Jakarta', -6.209, 106.846), 'MY': ('Kuala Lumpur', 3.139, 101.687), 'IL': ('Tel Aviv', 32.085, 34.782), 'ZA': ('Johannesburg', -26.106, 28.054),
        'AU': ('Sydney', -33.868, 151.209), 'NZ': ('Wellington', -41.287, 174.776), 'TR': ('Istanbul', 41.015, 28.979), 'SA': ('Riyadh', 24.713, 46.675),
        'SE': ('Stockholm', 59.333, 18.065), 'EG': ('Cairo', 30.044, 31.236)}
INDEX_CC = {'SPX': 'US', 'NDX': 'US', 'IXIC': 'US', 'DJI': 'US', 'RUT': 'US', 'VIX': 'US', 'TSX': 'CA', 'MXX': 'MX', 'IBOV': 'BR', 'MERV': 'AR', 'UKX': 'GB',
            'DAX': 'DE', 'CAC': 'FR', 'SX5E': 'EU', 'STOXX600': 'EU', 'SMI': 'CH', 'AEX': 'NL', 'IBEX': 'ES', 'FTSEMIB': 'IT', 'NKY': 'JP', 'TOPIX': 'JP',
            'SSEC': 'CN', 'SZSE': 'CN', 'HSI': 'HK', 'NIFTY': 'IN', 'SENSEX': 'IN', 'KOSPI': 'KR', 'TWII': 'TW', 'STI': 'SG', 'JKSE': 'ID', 'KLSE': 'MY',
            'TA125': 'IL', 'J203': 'ZA', 'XJO': 'AU', 'NZ50': 'NZ', 'BIST100': 'TR', 'TASI': 'SA', 'OMXS30': 'SE', 'EGX30': 'EG', 'ES1': 'US', 'YM1': 'US', 'NQ1': 'US'}

# Rates: id code -> (price source, name, country, how often the source publishes, name patterns)
RATES = {
    'US3M': ('^IRX', 'US 13-week Treasury bill yield', 'US', 'daily', [r'(us|u ?s|united states) (3|three).month (treasury )?(bill )?(yield|rate)', r'(13|thirteen).week treasury bill( yield)?']),
    'US02Y': ('FRED:DGS2', 'US 2-year Treasury yield', 'US', 'daily', [r'((us|u ?s|united states) )?(2|two).year (us )?treasur(y|ies)( note)?( yields?)?', r'(us|u ?s) (2|two).year (yield|note)']),
    'US05Y': ('^FVX', 'US 5-year Treasury yield', 'US', 'daily', [r'((us|u ?s|united states) )?(5|five).year (us )?treasur(y|ies)( note)?( yields?)?']),
    'US10Y': ('^TNX', 'US 10-year Treasury yield', 'US', 'daily', [r'((us|u ?s|united states) )?(10|ten).year (us )?treasur(y|ies)( note| bond)?( yields?)?', r'(us|u ?s) (10|ten).year (yield|note)', r'benchmark (us )?(10|ten).year (treasury )?yields?']),
    'US30Y': ('^TYX', 'US 30-year Treasury yield', 'US', 'daily', [r'((us|u ?s|united states) )?(30|thirty).year (us )?treasur(y|ies)( bond)?( yields?)?', r'(us|u ?s) (30|thirty).year (yield|bond)']),
}
for code, (series, freq) in FRED.items():
    if code in RATES or code in ('USIG', 'USHY'): continue
    cc = {'DE': 'DE', 'FR': 'FR', 'IT': 'IT', 'UK': 'GB', 'JP': 'JP', 'ES': 'ES', 'CH': 'CH', 'CA': 'CA', 'MX': 'MX', 'AU': 'AU', 'KR': 'KR', 'IN': 'IN', 'ZA': 'ZA', 'IL': 'IL'}[code[:2]]
    nm = {'DE': 'Germany 10-year Bund yield', 'FR': 'France 10-year OAT yield', 'IT': 'Italy 10-year BTP yield', 'GB': 'UK 10-year gilt yield', 'JP': 'Japan 10-year JGB yield'}.get(cc, f'{code[:2]} 10-year government bond yield')
    pats = {'DE': [r'(german|germany.?s?) (10|ten).year (bund|bond|government bond)s?( yields?)?', r'(10|ten).year bund( yields?)?', r'bund yields?'],
            'GB': [r'(uk|u ?k|british|britain.?s?) (10|ten).year (gilt|bond)s?( yields?)?', r'(10|ten).year gilt( yields?)?'],
            'JP': [r'(japan|japanese|japan.?s) (10|ten).year (jgb|government bond|bond)s?( yields?)?', r'(10|ten).year jgb( yields?)?'],
            'FR': [r'(french|france.?s?) (10|ten).year (oat|bond|government bond)s?( yields?)?'], 'IT': [r'(italian|italy.?s?) (10|ten).year (btp|bond|government bond)s?( yields?)?']}.get(cc, [])
    RATES[code] = ('FRED:' + series, nm, cc, freq, pats)
RATE_CITY = {'US': CITY['US'], 'GB': CITY['GB'], 'DE': CITY['DE'], 'FR': CITY['FR'], 'IT': ('Rome', 41.903, 12.496), 'JP': CITY['JP'], 'ES': CITY['ES'],
             'CH': ('Bern', 46.948, 7.447), 'CA': ('Ottawa', 45.421, -75.697), 'MX': CITY['MX'], 'AU': ('Canberra', -35.281, 149.13), 'KR': CITY['KR'],
             'IN': ('New Delhi', 28.614, 77.209), 'ZA': ('Pretoria', -25.747, 28.229), 'IL': ('Jerusalem', 31.769, 35.214)}

# Commodity name patterns by site symbol (markets.json carries the price symbol and place)
COMMODITY_NAMES = {
    'XAU': [r'gold( prices?| futures| bullion| spot)?', r'spot gold', r'xau'], 'XAG': [r'silver( prices?| futures)?', r'xag'],
    'WTI': [r'(wti|west texas intermediate)( crude)?( oil)?( prices?| futures)?', r'(us|u ?s) crude( oil)?( prices?| futures)?'],
    'BRENT': [r'brent( crude)?( oil)?( prices?| futures)?'], 'NG': [r'((us|u ?s|henry hub) )?natural gas( prices?| futures)?', r'henry hub( natural gas)?'],
    'HG': [r'copper( prices?| futures)?'], 'PL': [r'platinum( prices?| futures)?'], 'PA': [r'palladium( prices?| futures)?'],
    'ZW': [r'wheat( prices?| futures)?'], 'ZC': [r'corn( prices?| futures)?'], 'ZS': [r'soybeans?( prices?| futures)?'], 'KC': [r'(arabica )?coffee( prices?| futures)?'],
    'CC': [r'cocoa( prices?| futures)?'], 'SB': [r'(raw )?sugar( prices?| futures)?'], 'CT': [r'cotton( prices?| futures)?'], 'OJ': [r'orange juice( prices?| futures)?'],
    'ALI': [r'alumin(i)?um( prices?| futures)?'], 'HO': [r'heating oil( prices?| futures)?'], 'RB': [r'(rbob )?gasoline( prices?| futures)?'],
    'LE': [r'live cattle( prices?| futures)?'], 'HE': [r'lean hogs?( prices?| futures)?'], 'GF': [r'feeder cattle( prices?| futures)?'],
    'ZO': [r'oats?( prices?| futures)?'], 'ZR': [r'rough rice( prices?| futures)?'],
}
EXTRA_COMMODITIES = {'TTF': ('TTF=F', 'Dutch TTF natural gas', 'Amsterdam', 52.374, 4.89, [r'(dutch )?ttf( natural gas| gas)?( prices?| futures)?', r'european (natural )?gas( prices?| futures)?'])}
CRYPTO_NAMES = {'BTC': [r'bitcoin', r'btc'], 'ETH': [r'ethereum', r'ether', r'eth'], 'SOL': [r'solana'], 'XRP': [r'xrp', r'ripple.?s? xrp'], 'BNB': [r'bnb', r'binance coin'],
                'DOGE': [r'dogecoin'], 'ADA': [r'cardano'], 'TRX': [r'tron'], 'AVAX': [r'avalanche'], 'LINK': [r'chainlink'], 'LTC': [r'litecoin'], 'XLM': [r'stellar( lumens)?'],
                'BCH': [r'bitcoin cash'], 'ZEC': [r'zcash'], 'XMR': [r'monero'], 'SHIB': [r'shiba inu'], 'HYPE': [r'hyperliquid'], 'SUI': [r'sui'], 'HBAR': [r'hedera'],
                'USDT': [r'tether( usdt)?', r'usdt'], 'USDC': [r'usd coin', r'usdc'], 'DOT': [r'polkadot'], 'UNI': [r'uniswap'], 'AAVE': [r'aave'], 'NEAR': [r'near protocol']}
CRYPTO_EXTRA = {'DOT': 'Polkadot'}  # majors priced by update_news_prices but not in the site's coin list
# Company names whose usual form differs from the registrant's legal name; each points at one verified listing (its company's
# home listing is then chosen). Only unambiguous, well-known forms.
COMPANY_ALIASES = {'Google': 'GOOGL', 'Alphabet': 'GOOGL', 'Facebook': 'META', 'Meta': 'META', 'Berkshire Hathaway': 'BRK-B', 'TSMC': 'TSM',
                   'Taiwan Semiconductor': 'TSM', 'Samsung': '005930.KS', 'Samsung Electronics': '005930.KS', 'Alibaba': 'BABA', 'Tencent': '0700.HK',
                   'LVMH': 'MC.PA', 'Nestle': 'NESN.SW', 'Nestlé': 'NESN.SW', 'Roche': 'ROG.SW', 'Saudi Aramco': '2222.SR', 'Aramco': '2222.SR',
                   'Petrobras': 'PBR', 'Vale': 'VALE', 'BYD': '1211.HK', 'Xiaomi': '1810.HK', 'Toyota': '7203.T', 'Sony': '6758.T', 'SoftBank': '9984.T',
                   'SoftBank Group': '9984.T', 'Reliance': 'RELIANCE.NS', 'Reliance Industries': 'RELIANCE.NS', 'Rio Tinto': 'RIO', 'BHP': 'BHP',
                   'Shell': 'SHEL', 'BP': 'BP', 'HSBC': 'HSBC', 'Volkswagen': 'VOW3.DE', 'Mercedes-Benz': 'MBG.DE', 'BMW': 'BMW.DE', 'Siemens': 'SIE.DE',
                   'SAP': 'SAP', 'ASML': 'ASML', 'Novo Nordisk': 'NVO', 'Airbus': 'AIR.PA', 'JPMorgan': 'JPM', 'J.P. Morgan': 'JPM', 'Coca-Cola': 'KO',
                   'Walmart': 'WMT', 'Amazon': 'AMZN', 'Microsoft': 'MSFT', 'Nvidia': 'NVDA', 'Apple': 'AAPL', 'Tesla': 'TSLA', 'Netflix': 'NFLX',
                   'Goldman Sachs': 'GS', 'Morgan Stanley': 'MS', 'Citigroup': 'C', 'Citi': 'C', 'Bank of America': 'BAC', 'Wells Fargo': 'WFC',
                   'ExxonMobil': 'XOM', 'Exxon Mobil': 'XOM', 'Exxon': 'XOM', 'Chevron': 'CVX', 'Boeing': 'BA', 'Intel': 'INTC', 'AMD': 'AMD',
                   'Broadcom': 'AVGO', 'Oracle': 'ORCL', 'Salesforce': 'CRM', 'Pfizer': 'PFE', 'Eli Lilly': 'LLY', 'Moderna': 'MRNA', 'Uber': 'UBER',
                   'DoorDash': 'DASH', 'Instacart': 'CART', 'Coinbase': 'COIN', 'Robinhood': 'HOOD', 'Strategy': 'MSTR', 'MicroStrategy': 'MSTR'}

# Hand-checked: the Globe's display name is a well-known name of the company behind this exact symbol (official name differs).
CHECKED = {'ITX.MC': ('Inditex', 'Inditex = Industria de Diseño Textil'), 'FMX': ('FEMSA', 'FEMSA files with the SEC as Mexican Economic Development'),
           '2222.SR': ('Saudi Aramco', 'Saudi Aramco = Saudi Arabian Oil Company'), '2010.SR': ('SABIC', 'SABIC = Saudi Basic Industries Corporation'),
           'WALMEX.MX': ('Walmex', 'Walmex = Wal-Mart de México'), 'FEMSAUBD.MX': ('FEMSA', 'FEMSA = Fomento Económico Mexicano'),
           'THYAO.IS': ('Turkish Airlines', 'Turkish Airlines = Türk Hava Yolları'), 'PKO.WA': ('PKO Bank Polski', 'PKO = Powszechna Kasa Oszczędności'),
           'SQM-B.SN': ('SQM', 'SQM = Sociedad Química y Minera de Chile'), 'B3SA3.SA': ('B3', 'B3 = B3 S.A. - Brasil, Bolsa, Balcão'),
           'GE': ('GE Aerospace', 'GE Aerospace files with the SEC as General Electric Co')}

def site_assets():
    src = open(os.path.join(ROOT, 'assets', 'mock.js'), encoding='utf-8').read()
    out = {}
    for s, n, c in re.findall(r"\{ s: '([A-Z0-9]+)', n: '([^']+)'(?:, [a-z]+: '[^']*')*?, c: '([a-z]+)'", src): out[s] = (n, c)
    for s, n in re.findall(r"\bS\('([A-Z0-9]+)', '([^']+)'", src): out[s] = (n, 'stocks')
    return out

def news_tickers(extra_paths):
    """ticker -> Counter of names the news used with it; and the list of all names used without a ticker."""
    stories = []
    for p in [os.path.join(ROOT, 'assets/globe/news-live.json'), os.path.join(ROOT, 'assets/globe/news-archive.json')] + extra_paths:
        try:
            d = json.load(open(p, encoding='utf-8')); stories += d if isinstance(d, list) else d.get('stories', [])
        except Exception: pass
    for p in glob.glob(os.path.join(ROOT, 'assets/globe/events/*.json')):
        try:
            for e in json.load(open(p, encoding='utf-8')).get('events', []): stories.append({'impacts': e.get('assets', [])})
        except Exception: pass
    names = defaultdict(Counter)
    for s in stories:
        for r in (s.get('impacts') or []) + (s.get('entities') or []):
            t = R.norm_ticker(r.get('ticker') or r.get('t'))
            if t: names[t][r.get('name') or r.get('n') or ''] += 1
    return names

def untickered_names(extra_paths):
    out = set()
    for p in [os.path.join(ROOT, 'assets/globe/news-live.json'), os.path.join(ROOT, 'assets/globe/news-archive.json')] + extra_paths:
        try:
            d = json.load(open(p, encoding='utf-8'))
            for s in (d if isinstance(d, list) else d.get('stories', [])):
                for r in (s.get('impacts') or []) + (s.get('entities') or []):
                    if not r.get('ticker') and r.get('kind', 'company') == 'company' and r.get('name'): out.add(r['name'])
        except Exception: pass
    return out

def sec_place(cik, codes):
    """Headquarters from the SEC business address: {'la','lo','src','city','cc'}; la/lo None when the city is not in GeoNames."""
    sub = S.sec_submission(cik)
    if not sub: return None
    adr = sub.get('addresses') or {}
    a = adr.get('business') or {}
    if not a.get('stateOrCountry') and (adr.get('mailing') or {}).get('stateOrCountry'): a = {**adr['mailing'], 'city': a.get('city') or adr['mailing'].get('city')}
    city, st = re.split(r',', a.get('city') or '')[0].strip(), (a.get('stateOrCountry') or '').upper()
    if not city: return None
    if st in US_STATES: cc, ll = 'US', S.geocode(city, 'US', st)
    else:
        country = a.get('stateOrCountryDescription') or codes.get(st, '')
        country = country.split(',')[-1].strip() if ',' in country else country
        cc = COUNTRY_ISO.get(R.ascii_lower(country).strip()) if country else None
        ll = S.geocode(city, cc)
        if ll and not cc: cc = ll[2]
    return {'la': ll[0] if ll else None, 'lo': ll[1] if ll else None, 'src': 'sec-hq', 'city': re.sub(r'[0-9]+', '', city).strip().title(), 'cc': cc}

US_STATES = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR'.split())
COUNTRY_ISO = {}
ISO = {}

def build(history_paths=(), online=True):
    global COUNTRY_ISO
    for line in open(os.path.join(S.CACHE, 'countryInfo.txt'), encoding='utf-8') if os.path.exists(os.path.join(S.CACHE, 'countryInfo.txt')) else []:
        if line.startswith('#'): continue
        f = line.split('\t')
        if len(f) > 4: COUNTRY_ISO[R.ascii_lower(f[4]).strip()] = f[0]
    COUNTRY_ISO.update({'korea, republic of': 'KR', 'korea (south)': 'KR', 'republic of korea': 'KR', 'united kingdom': 'GB', 'cayman islands': 'KY',
                        'virgin islands, british': 'VG', 'taiwan, province of china': 'TW', 'netherlands': 'NL', 'russian federation': 'RU',
                        'iran, islamic republic of': 'IR', 'hong kong': 'HK', 'china': 'CN', 'macau': 'MO', 'bermuda': 'BM', 'jersey': 'JE', 'guernsey': 'GG'})
    codes = S.edgar_codes()
    ISO.update(json.load(open(os.path.join(ROOT, 'assets/globe/iso.json'), encoding='utf-8')))
    markets = json.load(open(os.path.join(ROOT, 'assets/globe/markets.json'), encoding='utf-8'))['assets']
    site = site_assets()
    site_by_y = {y: s for s, y in YAHOO.items()}
    assets, alias, names, companies, patterns, conflicts = {}, defaultdict(list), defaultdict(list), {}, [], []
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def add(aid, **a):
        a.setdefault('names', [])
        assets[aid] = {'id': aid, **a}
        return assets[aid]
    def al(t, aid):
        t = R.norm_ticker(t)
        if t and aid not in alias[t]: alias[t].append(aid)
    def nm(n, aid):
        k = R.name_key(n)
        if k and aid not in names[k]: names[k].append(aid)
    def pat(p, aid): patterns.append([p, aid])

    mk_by = {a['s']: a for a in markets}
    def mgeo(sym, src='markets'):
        m = mk_by.get(sym)
        return {'la': m['la'], 'lo': m['lo'], 'src': src, 'city': m.get('c')} if m and m.get('la') is not None else None

    # indices
    for code, (y, n, pats) in INDICES.items():
        cc = INDEX_CC[code]; c = CITY[cc]
        a = add(f'IX:{code}', **{'class': 'index', 'name': n, 'px': y, 'country': cc, 'site': next((s for s, yy in YAHOO.items() if yy == y), None) or (code if code in site else None),
                                 'geo': mgeo(y) or {'la': c[1], 'lo': c[2], 'src': 'market-centre', 'city': c[0]}, 'verify': {'method': 'fixed-table'}})
        for t in {y, code, y.lstrip('^'), a['site'] or ''}: al(t, a['id'])
        if code == 'SPX': al('^SPX', a['id']); al('.SPX', a['id']); al('SPX500', a['id'])
        if code == 'STOXX600': al('^STOXX600', a['id']); al('SXXP', a['id'])
        if code == 'NKY': al('N225', a['id']); al('^NKX', a['id'])
        nm(n, a['id'])
        for p in pats: pat(p, a['id'])
    for code, (y, n) in SITE_INDEX.items():
        c = CITY['US']
        a = add(f'IX:{code}', **{'class': 'index', 'name': n, 'px': y, 'country': 'US', 'site': code, 'geo': {'la': c[1], 'lo': c[2], 'src': 'market-centre', 'city': c[0]}, 'verify': {'method': 'fixed-table'}})
        al(y, a['id']); al(code, a['id'])
    # currencies: one concept per Globe pair, in the site's convention (change = strength of the named currency against the US dollar)
    for m in markets:
        if m['t'] != 'fx': continue
        s = m['s']; aid = f'FX:{s}'
        add(aid, **{'class': 'fx', 'name': m['n'], 'px': s, 'country': None, 'site': s if s in site else None, 'geo': mgeo(s), 'verify': {'method': 'fixed-table'},
                    'note': m.get('note') or None})
        al(s, aid); al(s + '=X', aid); al(s[:3] + '/' + s[3:], aid)
        if s.startswith('USD') and len(s) == 6:
            ccy = s[3:]; al(ccy + '=X', aid); al(ccy + 'USD', aid); al(ccy + 'USD=X', aid); al(ccy + '/USD', aid)
            pat(re.escape(R.ascii_lower(m['n'])) + r's?( \(' + ccy.lower() + r'\))?', aid); pat(ccy.lower(), aid)
        elif s.endswith('USD') and len(s) == 6:
            ccy = s[:3]; al('USD' + ccy, aid); al('USD' + ccy + '=X', aid); al(ccy + '=X', aid); al('USD/' + ccy, aid)
            pat(re.escape(R.ascii_lower(m['n'])) + r'( \(' + ccy.lower() + r'\))?', aid); pat(ccy.lower(), aid)
    add('FX:DXY', **{'class': 'fx', 'name': 'US Dollar Index', 'px': 'DX-Y.NYB', 'country': 'US', 'site': 'DXY', 'geo': {'la': NY[0], 'lo': NY[1], 'src': 'market-centre', 'city': 'New York'},
                     'verify': {'method': 'fixed-table'}})
    for t in ('DXY', 'DX-Y.NYB', 'DX=F', 'USDX', '^DXY'): al(t, 'FX:DXY')
    for p in (r'(the )?(us|u ?s) dollar index', r'dxy', r'(ice )?dollar index'): pat(p, 'FX:DXY')
    # crypto: the site's coin list (priced as <SYM>-USD), drawn at the Globe's crypto hub; stablecoins keep the issuer place the Globe already uses
    coins = {s: n for s, (n, c) in site.items() if c == 'crypto'}; coins.update(CRYPTO_EXTRA)
    for m in markets:
        if m['t'] == 'crypto': coins.setdefault(m['s'], m['n'])
    for sym, n in coins.items():
        aid = f'CR:{sym}'; y = YAHOO.get(sym, sym + '-USD')
        add(aid, **{'class': 'crypto', 'name': n, 'px': y, 'site': sym if sym in site else None,
                    'geo': mgeo(sym) or {'la': 0, 'lo': -30, 'src': 'hub', 'city': None}, 'verify': {'method': 'fixed-table'}})
        for t in {sym, y, sym + '-USD', sym + 'USD', sym + '-USDT', sym + 'USDT', sym + '/USD'}: al(t, aid)
        for p in CRYPTO_NAMES.get(sym, [re.escape(R.ascii_lower(n))]): pat(p, aid)
    al('XBT', 'CR:BTC'); al('XBTUSD', 'CR:BTC')
    # commodities: the Globe's futures
    for m in markets:
        if m['t'] != 'cmd': continue
        code = m.get('site') or m['s'].replace('=F', ''); aid = f'CM:{code}'
        add(aid, **{'class': 'commodity', 'name': m['n'], 'px': m['s'], 'site': code if code in site else None, 'geo': mgeo(m['s']), 'verify': {'method': 'fixed-table'}, 'unit': m.get('u') or None})
        for t in {m['s'], code}: al(t, aid)
        if code in ('XAU', 'XAG', 'PL', 'PA'): al(code + 'USD', aid); al(code + 'USD=X', aid); al(code + '=X', aid)
        for p in COMMODITY_NAMES.get(code, [re.escape(R.ascii_lower(m['n']))]): pat(p, aid)
    for code, (y, n, city, la, lo, pats) in EXTRA_COMMODITIES.items():
        aid = f'CM:{code}'
        add(aid, **{'class': 'commodity', 'name': n, 'px': y, 'site': None, 'geo': {'la': la, 'lo': lo, 'src': 'market-centre', 'city': city}, 'verify': {'method': 'yahoo-record'}})
        al(y, aid); al(code, aid)
        for p in pats: pat(p, aid)
    # rates
    for code, (px, n, cc, freq, pats) in RATES.items():
        aid = f'RT:{code}'; c = RATE_CITY[cc]
        add(aid, **{'class': 'rate', 'name': n, 'px': px, 'freq': freq, 'country': cc, 'site': code if code in site else None,
                    'geo': {'la': c[1], 'lo': c[2], 'src': 'issuer-capital' if cc != 'US' else 'market-centre', 'city': c[0]}, 'verify': {'method': 'fixed-table'}})
        al(code, aid)
        if px.startswith('^'): al(px, aid); al(px.lstrip('^'), aid)
        if code == 'US10Y': al('US10YT=X', aid); al('US10Y=X', aid); al('TNX', aid)
        for p in pats: pat(p, aid)

    # ---------- equities and funds ----------
    sec = S.sec_tickers()
    sec_by = {}
    for r in sec:
        if r['ticker'] and r['exchange']: sec_by.setdefault(r['ticker'].upper(), r)
    sec_first = {}
    for r in sec:
        if r['exchange']: sec_first.setdefault(r['cik'], r['ticker'].upper())
    used = news_tickers(list(history_paths))
    want = set(used)
    for m in markets:
        if m['t'] == 'stocks' and m.get('g') != 'Index': want.add(YAHOO.get(m.get('site') or '', m['s']))
    for s, (n, c) in site.items():
        if c in ('stocks', 'funds', 'reits'): want.add(YAHOO.get(s, s))
    want |= {t for t in COMPANY_ALIASES.values()}
    want = {w for w in want if w}
    fixed_alias = set(alias)
    def eq_from_sec(t):
        r = sec_by.get(t.replace('.', '-')) or sec_by.get(t)
        if not r: return None
        mic = SEC_MIC.get(r['exchange'], 'XXXX'); sym = r['ticker'].upper(); aid = f'EQ:{mic}:{sym}'
        if aid in assets: return aid
        cik = f"{int(r['cik']):010d}"
        add(aid, **{'class': 'equity', 'name': smart_title(r['name']), 'official': r['name'], 'sym': sym, 'mic': mic, 'px': sym, 'cik': cik, 'company': f'CO:CIK{cik}',
                    'primary': sec_first.get(r['cik']) == sym, 'verify': {'method': 'sec-company-tickers', 'at': now}})
        for v in {sym, sym.replace('-', '.'), sym.replace('-', '/'), sym.replace('-', '')} if '-' in sym else {sym}: al(v, aid)
        return aid
    def eq_from_yahoo(t):
        if t.startswith('^') or '=' in t: return None
        m = S.yahoo_meta(t) if online or os.path.exists(os.path.join(S.CACHE, 'yahoo', re.sub(r'[^A-Za-z0-9._=^-]', '_', t) + '.json')) else None
        if not m or m.get('instrumentType') not in ('EQUITY', 'ETF', 'MUTUALFUND'): return None
        v = VENUES.get(m.get('exchangeName'))
        if not v: return None
        off = m.get('longName') or m.get('shortName')
        if not off: return None
        mic, city, la, lo, cc = v
        if mic == 'OTCM': la = lo = None  # an over-the-counter line says nothing about where the company is
        sym = t.rsplit('.', 1)[0] if '.' in t and cc != 'US' else t  # exchange suffix off; US class shares (BRK.B) keep theirs
        aid = f'EQ:{mic}:{sym}'
        if aid in assets: al(t, aid); return aid
        add(aid, **{'class': 'fund' if m['instrumentType'] != 'EQUITY' else 'equity', 'name': smart_title(m.get('shortName') or off) if not m.get('longName') else smart_title(off),
                    'official': off, 'names': [m['shortName']] if m.get('shortName') and m.get('shortName') != off else [], 'sym': sym, 'mic': mic, 'px': t,
                    'country': cc if mic != 'OTCM' else None, 'currency': m.get('currency'), 'geo': {'la': la, 'lo': lo, 'src': 'listing-venue', 'city': city} if la is not None else None,
                    'verify': {'method': 'yahoo-security-record', 'at': now}})
        al(t, aid)
        return aid
    sec_names = defaultdict(set)
    for r in sec:
        if r['exchange'] and r['exchange'] != 'OTC': sec_names[R.name_key(r['name'])].add(r['cik'])
    for n in sorted(untickered_names(list(history_paths))):
        ciks = sec_names.get(R.name_key(n), set())
        if len(ciks) == 1 and len(R.name_key(n)) >= 3: want.add(sec_first[next(iter(ciks))])
    for t in sorted(want):
        if t in fixed_alias: continue
        if '.' not in t or re.fullmatch(r'[A-Z]+\.[A-Z]', t):
            if eq_from_sec(t): continue
        eq_from_yahoo(t)
    # ETFs and funds that are SEC registrants still need the Yahoo record to know they are funds; equities from SEC: instrument stays 'equity'
    # Globe places and site symbols for listings; a Globe asset whose name is another company's is a conflict, never merged
    for m in markets:
        if m['t'] != 'stocks' or m.get('g') == 'Index': continue
        y = YAHOO.get(m.get('site') or '', m['s'])
        ids = [i for i in alias.get(R.norm_ticker(y), []) if i.startswith('EQ:')]
        if not ids:
            conflicts.append({'globe': m['s'], 'name': m['n'], 'issue': 'unverified', 'yahoo': y}); continue
        aid = ids[0]; a = assets[aid]
        if CHECKED.get(y, ('',))[0] == m['n']: a['names'] = sorted(set(a['names']) | {m['n']}); a['checked'] = CHECKED[y][1]
        if not R.same_company(m['n'], a.get('official') or a['name']) and m['n'] not in a['names'] and not any(R.same_company(m['n'], x) for x in a['names']):
            conflicts.append({'globe': m['s'], 'name': m['n'], 'issue': 'name-mismatch', 'yahoo': y, 'official': a.get('official')}); continue
        a['geo'] = mgeo(m['s']); a['names'] = sorted(set(a['names']) | {m['n']})
        if ISO.get(m.get('k')): a['country'] = ISO[m['k']]
        if m.get('site'): a['site'] = m['site']
        if y != m['s']: a.setdefault('globe_symbol', m['s'])
        if m['s'] != y:
            al(m['s'], aid)  # the Globe/site symbol (e.g. MC for LVMH) is an alias, never the ticker...
            eq_from_sec(m['s'])  # ...and the same letters keep their real meaning (MC = Moelis & Company): the name decides
    for s, (n, c) in site.items():
        if c not in ('stocks', 'funds', 'reits'): continue
        ids = [i for i in alias.get(R.norm_ticker(YAHOO.get(s, s)), []) if i.startswith('EQ:')]
        if ids and R.same_company(n, assets[ids[0]].get('official') or assets[ids[0]]['name']):
            assets[ids[0]]['site'] = s; assets[ids[0]]['names'] = sorted(set(assets[ids[0]]['names']) | {n}); al(s, ids[0])
    # headquarters for US registrants the Globe has no place for (SEC business address -> GeoNames)
    need = [a for a in assets.values() if a['id'].startswith('EQ:') and a.get('cik') and not a.get('geo')]
    with ThreadPoolExecutor(4) as ex: places = list(ex.map(lambda a: sec_place(a['cik'], codes) if online or os.path.exists(os.path.join(S.CACHE, 'sec', a['cik'] + '.json')) else None, need))
    for a, g in zip(need, places):
        if g:
            a['country'] = g.pop('cc')
            if g['la'] is not None: a['geo'] = g
    # companies: SEC CIK, or the listing itself; listings of one company are linked only when their official names are the same name
    by_key = defaultdict(list)
    for a in assets.values():
        if a['class'] in ('equity', 'fund'):
            a.setdefault('company', f"CO:{a['id']}")
            by_key[R.name_key(a.get('official') or a['name'])].append(a['id'])
    for k, ids in by_key.items():
        cos = {assets[i]['company'] for i in ids}
        same_full = len({' '.join(R.words(assets[i].get('official') or assets[i]['name'], True)) for i in ids}) == 1
        if len(ids) > 1 and len([c for c in cos if c.startswith('CO:CIK')]) <= 1 and (len(k) >= 4 or same_full):
            co = next((c for c in cos if c.startswith('CO:CIK')), sorted(cos)[0])
            for i in ids: assets[i]['company'] = co
    for a in assets.values():
        if a['class'] not in ('equity', 'fund'): continue
        c = companies.setdefault(a['company'], {'id': a['company'], 'name': a['name'], 'listings': []})
        c['listings'].append(a['id'])
        if a.get('cik'): c['cik'] = a['cik']; c['name'] = a['name']
    for c in companies.values():  # home listing: the one in the company's own country, else the SEC primary, else the first
        ls = [assets[i] for i in c['listings']]
        hq = (sec_place(c['cik'], codes) or {}).get('cc') if c.get('cik') and len(ls) > 1 else None
        hq = hq or next((l.get('country') for l in ls if l.get('geo') and l['geo'].get('src') in ('sec-hq', 'markets')), None)
        home = next((l for l in ls if l.get('mic') and VENUE_CC.get(l['mic']) == hq and len(ls) > 1), None) or next((l for l in ls if l.get('primary')), None) or ls[0]
        home['home'] = True
        c['home'] = home['id']
    for a in assets.values():
        if a['class'] in ('equity', 'fund'):
            for n in [a['name'], a.get('official')] + a['names']: nm(n or '', a['id'])
    for n, t in COMPANY_ALIASES.items():
        ids = [i for i in alias.get(R.norm_ticker(t), []) if i.startswith('EQ:')]
        if ids:
            for i in companies[assets[ids[0]]['company']]['listings']: nm(n, i)
    # names shared by different companies are ambiguous: dropped from the name index (the ticker path still works)
    names = {k: v for k, v in names.items() if len({assets[i].get('company') or i for i in v}) == 1}
    reg = {'schema': 'investedia.registry/v1', 'version': R.VERSION, 'built_at': now,
           'sources': {'sec': 'https://www.sec.gov/files/company_tickers_exchange.json (+ submissions business address)', 'yahoo': 'Yahoo Finance chart meta (official security name, exchange, type)',
                       'geonames': 'GeoNames cities15000 (CC BY 4.0)', 'globe': 'assets/globe/markets.json', 'site': 'assets/mock.js + update_market.YAHOO'},
           'counts': dict(Counter(a['class'] for a in assets.values())), 'assets': dict(sorted(assets.items())), 'companies': dict(sorted(companies.items())),
           'alias': dict(sorted(alias.items())), 'names': dict(sorted(names.items())), 'patterns': patterns, 'conflicts': conflicts}
    return reg

VENUE_CC = {v[0]: v[4] for v in VENUES.values()}
VENUE_CC.update({'XNYS': 'US', 'XNAS': 'US', 'BATS': 'US', 'OTCM': 'US', 'XTXS': 'US'})

def smart_title(n):
    n = re.sub(r'\s+', ' ', str(n or '')).strip()
    if n.isupper() or n.islower():
        keep = {'ASA', 'ADR', 'NV', 'SA', 'AG', 'SE', 'PLC', 'LLC', 'LP', 'ETF', 'REIT', 'USA', 'US', 'UK', 'II', 'III', 'IBM', 'AT&T', 'NVIDIA', 'AMD', 'HSBC', 'BP', 'UBS', 'ING', 'ASML', 'SAP'}
        n = ' '.join(w if w in keep else w.capitalize() for w in n.split())
    n = re.sub(r'[,]?\s+(Inc\.?|Corp\.?|Corporation|Co\.?|Ltd\.?|Limited|Plc|PLC|Holdings,? Inc\.?|N\.?V\.?|S\.?A\.?|AG|SE|/[A-Z]{2}/?|/)$', '', n).strip(' ,/')
    return n

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--history', action='append', default=[]); ap.add_argument('--offline', action='store_true')
    a = ap.parse_args()
    reg = build(a.history, online=not a.offline)
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(R.PATH, 'w', encoding='utf-8') as f: json.dump(reg, f, ensure_ascii=False, separators=(',', ':'))
    print(reg['counts'], 'aliases', len(reg['alias']), 'names', len(reg['names']), 'patterns', len(reg['patterns']), 'conflicts', len(reg['conflicts']),
          f"{os.path.getsize(R.PATH) / 1e6:.2f} MB")
