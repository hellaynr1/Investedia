// Asset list and page content. Real prices come from assets/quotes.js (written by update_market.py);
// anything without a real feed falls back to the sample values below.
window.MOCK = (function () {
  // Deterministic random generator so every chart looks the same on each visit
  function seeded(str) {
    let h = 1779033703 ^ str.length;
    for (let i = 0; i < str.length; i++) { h = Math.imul(h ^ str.charCodeAt(i), 3432918353); h = h << 13 | h >>> 19; }
    return function () { h = Math.imul(h ^ h >>> 16, 2246822507); h = Math.imul(h ^ h >>> 13, 3266489909); h ^= h >>> 16; return (h >>> 0) / 4294967296; };
  }
  // Random-walk price series ending at `last`, with an overall drift of `chg` percent
  function series(key, n, last, chg, vol = 0.012) {
    const r = seeded(key + n), out = new Array(n);
    let v = 1;
    for (let i = 0; i < n; i++) { v *= 1 + (r() - 0.5) * 2 * vol; out[i] = v; }
    const start = last / (1 + chg / 100), drift = (last / start);
    return out.map((x, i) => { const t = i / (n - 1); const base = start * Math.pow(drift, t); return base * x / Math.pow(out[n - 1], t); });
  }

  const assets = [
    // stocks
    { s: 'NVDA', n: 'NVIDIA Corp', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 217.23, d: -1.84, w: 3.2, m: 5240, pe: 27.5, vol: '127.0M', logo: '#76b900' },
    { s: 'AAPL', n: 'Apple Inc', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 342.00, d: -0.28, w: 1.1, m: 5080, pe: 38.1, vol: '41.2M', logo: '#d4d4d8' },
    { s: 'MSFT', n: 'Microsoft Corp', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 539.44, d: 1.08, w: 2.4, m: 4010, pe: 36.4, vol: '19.8M', logo: '#00a4ef' },
    { s: 'AMZN', n: 'Amazon.com Inc', x: 'NASDAQ', c: 'stocks', sector: 'Consumer', p: 254.76, d: 0.27, w: -0.6, m: 2710, pe: 41.7, vol: '38.5M', logo: '#ff9900' },
    { s: 'GOOGL', n: 'Alphabet Inc', x: 'NASDAQ', c: 'stocks', sector: 'Communication', p: 349.22, d: 0.45, w: 4.1, m: 4240, pe: 29.9, vol: '27.3M', logo: '#4285f4' },
    { s: 'META', n: 'Meta Platforms', x: 'NASDAQ', c: 'stocks', sector: 'Communication', p: 736.72, d: -0.11, w: 1.9, m: 1860, pe: 27.0, vol: '11.6M', logo: '#0866ff' },
    { s: 'TSLA', n: 'Tesla Inc', x: 'NASDAQ', c: 'stocks', sector: 'Consumer', p: 362.44, d: -1.29, w: -5.2, m: 1170, pe: 168.2, vol: '96.1M', logo: '#e31937' },
    { s: 'AVGO', n: 'Broadcom Inc', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 412.80, d: -0.55, w: 2.7, m: 1940, pe: 71.3, vol: '18.4M', logo: '#cc092f' },
    { s: 'JPM', n: 'JPMorgan Chase', x: 'NYSE', c: 'stocks', sector: 'Finance', p: 318.65, d: 0.07, w: 1.2, m: 880, pe: 15.8, vol: '8.9M', logo: '#a3a3a3' },
    { s: 'LLY', n: 'Eli Lilly', x: 'NYSE', c: 'stocks', sector: 'Healthcare', p: 1012.40, d: 3.55, w: 6.8, m: 960, pe: 58.2, vol: '5.1M', logo: '#d52b1e' },
    { s: 'XOM', n: 'Exxon Mobil', x: 'NYSE', c: 'stocks', sector: 'Energy', p: 118.22, d: -1.32, w: -2.4, m: 505, pe: 14.1, vol: '14.7M', logo: '#ed1b2f' },
    { s: 'V', n: 'Visa Inc', x: 'NYSE', c: 'stocks', sector: 'Finance', p: 381.10, d: 2.13, w: 3.0, m: 742, pe: 32.6, vol: '7.2M', logo: '#1a1f71' },
    { s: 'DELL', n: 'Dell Technologies', x: 'NYSE', c: 'stocks', sector: 'Technology', p: 128.35, d: -6.80, w: -9.1, m: 89, pe: 19.4, vol: '22.8M', logo: '#007db8' },
    { s: 'WULF', n: 'TeraWulf Inc', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 12.62, d: 9.36, w: 18.2, m: 5, pe: null, vol: '64.0M', logo: '#3b82f6' },
    { s: 'CRWV', n: 'CoreWeave Inc', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 69.69, d: 5.94, w: 11.4, m: 34, pe: null, vol: '31.5M', logo: '#a855f7' },
    { s: 'INTC', n: 'Intel Corp', x: 'NASDAQ', c: 'stocks', sector: 'Technology', p: 95.37, d: -2.80, w: -4.6, m: 416, pe: 88.0, vol: '58.3M', logo: '#0071c5' },
    // indices
    { s: 'SPX', n: 'S&P 500', x: 'INDEX', c: 'indices', p: 7732.5, d: -0.08, w: 0.9, logo: '#ff7a1a' },
    { s: 'NDX', n: 'Nasdaq 100', x: 'INDEX', c: 'indices', p: 29793.5, d: -0.26, w: 1.3, logo: '#0ea5e9' },
    { s: 'DJI', n: 'Dow Jones 30', x: 'INDEX', c: 'indices', p: 52158.6, d: -0.05, w: 0.4, logo: '#a1a1aa' },
    { s: 'RUT', n: 'Russell 2000', x: 'INDEX', c: 'indices', p: 2741.2, d: 0.62, w: 2.1, logo: '#22c55e' },
    { s: 'DAX', n: 'DAX 40', x: 'INDEX', c: 'indices', p: 25298.6, d: 0.15, w: 0.7, logo: '#eab308' },
    { s: 'CAC', n: 'CAC 40', x: 'INDEX', c: 'indices', p: 8412.9, d: 0.31, w: 1.0, logo: '#3b82f6' },
    { s: 'UKX', n: 'FTSE 100', x: 'INDEX', c: 'indices', p: 9688.4, d: -0.12, w: 0.2, logo: '#ef4444' },
    { s: 'NKY', n: 'Nikkei 225', x: 'INDEX', c: 'indices', p: 67744.3, d: -0.05, w: 3.4, logo: '#f43f5e' },
    // crypto
    { s: 'BTC', n: 'Bitcoin', x: 'CRYPTO', c: 'crypto', p: 82147.06, d: 0.65, w: -4.8, m: 1630, vol: '$38.2B', logo: '#f7931a' },
    { s: 'ETH', n: 'Ethereum', x: 'CRYPTO', c: 'crypto', p: 2439.45, d: 0.80, w: -7.1, m: 294, vol: '$17.4B', logo: '#627eea' },
    { s: 'SOL', n: 'Solana', x: 'CRYPTO', c: 'crypto', p: 168.40, d: 2.41, w: -3.3, m: 92, vol: '$4.1B', logo: '#14f195' },
    { s: 'XRP', n: 'XRP', x: 'CRYPTO', c: 'crypto', p: 2.31, d: -1.12, w: -6.0, m: 138, vol: '$3.2B', logo: '#23292f' },
    { s: 'BNB', n: 'BNB', x: 'CRYPTO', c: 'crypto', p: 914.20, d: 0.33, w: 1.4, m: 128, vol: '$1.9B', logo: '#f3ba2f' },
    { s: 'DOGE', n: 'Dogecoin', x: 'CRYPTO', c: 'crypto', p: 0.1987, d: 4.02, w: 2.2, m: 30, vol: '$1.6B', logo: '#c2a633' },
    // currencies
    { s: 'EURUSD', n: 'Euro / US Dollar', x: 'FX', c: 'currencies', p: 1.1642, d: 0.18, w: 0.4, logo: '#3b82f6' },
    { s: 'GBPUSD', n: 'British Pound / US Dollar', x: 'FX', c: 'currencies', p: 1.3384, d: -0.09, w: -0.3, logo: '#ef4444' },
    { s: 'USDJPY', n: 'US Dollar / Japanese Yen', x: 'FX', c: 'currencies', p: 151.82, d: 0.24, w: 0.9, logo: '#f43f5e' },
    { s: 'USDCHF', n: 'US Dollar / Swiss Franc', x: 'FX', c: 'currencies', p: 0.7968, d: -0.15, w: -0.2, logo: '#dc2626' },
    { s: 'AUDUSD', n: 'Australian Dollar / US Dollar', x: 'FX', c: 'currencies', p: 0.6612, d: 0.41, w: 0.6, logo: '#2563eb' },
    { s: 'DXY', n: 'US Dollar Index', x: 'FX', c: 'currencies', p: 98.42, d: -0.11, w: -0.5, logo: '#22c55e' },
    // commodities
    { s: 'XAU', n: 'Gold', x: 'COMEX', c: 'commodities', p: 4128.60, d: 0.92, w: 2.8, unit: '/oz', logo: '#eab308' },
    { s: 'XAG', n: 'Silver', x: 'COMEX', c: 'commodities', p: 51.84, d: 1.47, w: 4.0, unit: '/oz', logo: '#cbd5e1' },
    { s: 'WTI', n: 'Crude Oil WTI', x: 'NYMEX', c: 'commodities', p: 61.37, d: -1.65, w: -3.9, unit: '/bbl', logo: '#78716c' },
    { s: 'BRENT', n: 'Brent Crude', x: 'ICE', c: 'commodities', p: 65.02, d: -1.41, w: -3.5, unit: '/bbl', logo: '#57534e' },
    { s: 'NG', n: 'Natural Gas', x: 'NYMEX', c: 'commodities', p: 3.12, d: 2.30, w: 6.1, unit: '/MMBtu', logo: '#38bdf8' },
    { s: 'HG', n: 'Copper', x: 'COMEX', c: 'commodities', p: 5.03, d: 0.58, w: 1.7, unit: '/lb', logo: '#c2410c' },
    // bonds (p = yield %)
    { s: 'US02Y', n: 'US 2-Year Treasury', x: 'BOND', c: 'bonds', p: 3.482, d: -0.6, w: -1.8, y: true, logo: '#64748b' },
    { s: 'US10Y', n: 'US 10-Year Treasury', x: 'BOND', c: 'bonds', p: 4.031, d: -0.4, w: -1.1, y: true, logo: '#64748b' },
    { s: 'US30Y', n: 'US 30-Year Treasury', x: 'BOND', c: 'bonds', p: 4.612, d: -0.2, w: -0.6, y: true, logo: '#64748b' },
    { s: 'DE10Y', n: 'Germany 10-Year Bund', x: 'BOND', c: 'bonds', p: 2.612, d: 0.3, w: 0.8, y: true, logo: '#64748b' },
    { s: 'FR10Y', n: 'France 10-Year OAT', x: 'BOND', c: 'bonds', p: 3.384, d: 0.5, w: 1.2, y: true, logo: '#64748b' },
    { s: 'JP10Y', n: 'Japan 10-Year JGB', x: 'BOND', c: 'bonds', p: 1.672, d: 1.1, w: 2.9, y: true, logo: '#64748b' },
    // funds
    { s: 'SPY', n: 'SPDR S&P 500 ETF', x: 'NYSE ARCA', c: 'funds', p: 771.79, d: -0.09, w: 0.9, aum: '$684B', fee: '0.09%', logo: '#ff7a1a' },
    { s: 'QQQ', n: 'Invesco QQQ Trust', x: 'NASDAQ', c: 'funds', p: 728.00, d: -0.27, w: 1.3, aum: '$362B', fee: '0.20%', logo: '#0ea5e9' },
    { s: 'VTI', n: 'Vanguard Total Stock Market', x: 'NYSE ARCA', c: 'funds', p: 342.15, d: -0.04, w: 1.0, aum: '$512B', fee: '0.03%', logo: '#b91c1c' },
    { s: 'VWCE', n: 'Vanguard FTSE All-World', x: 'XETRA', c: 'funds', p: 148.62, d: 0.21, w: 0.8, aum: '€24B', fee: '0.19%', logo: '#b91c1c' },
    { s: 'IBIT', n: 'iShares Bitcoin Trust', x: 'NASDAQ', c: 'funds', p: 47.06, d: 0.61, w: -4.9, aum: '$91B', fee: '0.25%', logo: '#000' },
    { s: 'GLD', n: 'SPDR Gold Shares', x: 'NYSE ARCA', c: 'funds', p: 381.40, d: 0.88, w: 2.7, aum: '$128B', fee: '0.40%', logo: '#eab308' },
  ];
  // Extra assets referenced by menus, category pages and the screener
  const S = (s, n, x, sector, country, p, d, w, m, pe, g, dv, logo) => ({ s, n, x, c: 'stocks', sector, country, p, d, w, m, pe, g, div: dv, vol: (Math.abs(d) * 9 + 3).toFixed(1) + 'M', logo, ext: true });
  assets.push(
    S('NFLX', 'Netflix Inc', 'NASDAQ', 'Communication', 'US', 72.61, 1.24, 2.2, 309, 42.8, 15.9, 0, '#e50914'),
    S('AMD', 'Advanced Micro Devices', 'NASDAQ', 'Technology', 'US', 238.40, -2.16, 4.8, 387, 96.1, 31.7, 0, '#ed1c24'),
    S('BA', 'Boeing Co', 'NYSE', 'Industrials', 'US', 214.75, 0.88, -1.2, 162, null, 24.6, 0, '#0033a1'),
    S('GME', 'GameStop Corp', 'NYSE', 'Consumer', 'US', 24.18, 6.42, 12.4, 11, 98.0, -8.4, 0, '#ef4444'),
    S('ORCL', 'Oracle Corp', 'NYSE', 'Technology', 'US', 291.30, 1.75, 5.1, 818, 58.4, 17.2, 0.7, '#c74634'),
    S('CRM', 'Salesforce Inc', 'NYSE', 'Technology', 'US', 248.10, -0.62, -2.0, 237, 38.9, 9.8, 0.7, '#00a1e0'),
    S('ADBE', 'Adobe Inc', 'NASDAQ', 'Technology', 'US', 352.85, -0.44, -1.6, 150, 22.1, 10.6, 0, '#fa0f00'),
    S('ASML', 'ASML Holding', 'NASDAQ', 'Technology', 'NL', 1018.20, 0.92, 3.9, 401, 37.8, 15.4, 0.7, '#0f238c'),
    S('TSM', 'Taiwan Semiconductor', 'NYSE', 'Technology', 'TW', 302.60, -0.71, 2.5, 1570, 26.9, 38.2, 1.1, '#c4161c'),
    S('SAP', 'SAP SE', 'XETRA', 'Technology', 'DE', 231.45, 0.38, 0.8, 270, 41.2, 11.1, 1.0, '#0faaff'),
    S('KO', 'Coca-Cola Co', 'NYSE', 'Consumer', 'US', 68.94, 0.21, 0.6, 297, 23.4, 4.8, 3.0, '#f40009'),
    S('PEP', 'PepsiCo Inc', 'NASDAQ', 'Consumer', 'US', 151.20, -0.18, 0.4, 207, 22.6, 1.7, 3.7, '#004b93'),
    S('WMT', 'Walmart Inc', 'NASDAQ', 'Consumer', 'US', 104.82, 0.66, 1.9, 838, 39.5, 4.9, 0.9, '#0071ce'),
    S('COST', 'Costco Wholesale', 'NASDAQ', 'Consumer', 'US', 921.40, 0.12, -0.5, 409, 50.8, 8.1, 0.6, '#e31837'),
    S('BAC', 'Bank of America', 'NYSE', 'Finance', 'US', 52.36, 0.93, 2.7, 393, 14.2, 7.4, 2.1, '#e31837'),
    S('WFC', 'Wells Fargo', 'NYSE', 'Finance', 'US', 84.17, 1.14, 3.3, 274, 13.6, 3.2, 2.0, '#d71e28'),
    S('GS', 'Goldman Sachs', 'NYSE', 'Finance', 'US', 801.55, 0.47, 2.0, 246, 16.9, 12.6, 1.6, '#7399c6'),
    S('HSBA', 'HSBC Holdings', 'LSE', 'Finance', 'UK', 10.42, 0.35, 1.1, 182, 9.4, 5.8, 5.9, '#db0011'),
    S('BNP', 'BNP Paribas', 'EURONEXT', 'Finance', 'FR', 78.90, 0.58, 1.5, 89, 7.6, 4.1, 6.3, '#00915a'),
    S('UNH', 'UnitedHealth Group', 'NYSE', 'Healthcare', 'US', 356.20, -0.84, -3.1, 323, 15.8, 7.7, 2.5, '#002677'),
    S('JNJ', 'Johnson & Johnson', 'NYSE', 'Healthcare', 'US', 187.65, 0.29, 1.0, 452, 18.1, 5.2, 2.8, '#d51900'),
    S('NVO', 'Novo Nordisk', 'NYSE', 'Healthcare', 'DK', 54.30, -1.72, -4.4, 242, 15.3, 10.9, 3.1, '#001965'),
    S('PFE', 'Pfizer Inc', 'NYSE', 'Healthcare', 'US', 25.84, -0.31, -0.7, 147, 13.7, -1.9, 6.6, '#0093d0'),
    S('CVX', 'Chevron Corp', 'NYSE', 'Energy', 'US', 152.40, -1.09, -2.6, 265, 17.4, -3.8, 4.5, '#0054a4'),
    S('SHEL', 'Shell plc', 'LSE', 'Energy', 'UK', 71.22, -1.25, -2.9, 214, 13.0, -5.2, 3.9, '#fbce07'),
    S('TTE', 'TotalEnergies', 'EURONEXT', 'Energy', 'FR', 55.84, -0.96, -2.2, 124, 9.8, -4.6, 5.6, '#ed1c24'),
    S('NEE', 'NextEra Energy', 'NYSE', 'Utilities', 'US', 83.65, 0.74, 2.4, 172, 26.3, 8.8, 2.7, '#00a3e0'),
    S('ENPH', 'Enphase Energy', 'NASDAQ', 'Utilities', 'US', 36.90, 2.81, 6.5, 5, 28.4, -12.3, 0, '#f37321'),
    S('FSLR', 'First Solar', 'NASDAQ', 'Utilities', 'US', 241.15, 1.96, 4.2, 26, 19.7, 23.5, 0, '#e2231a'),
    S('MC', 'LVMH', 'EURONEXT', 'Consumer', 'FR', 598.40, 0.52, 1.8, 299, 25.1, -2.0, 2.2, '#9a7b4f'),
    S('TM', 'Toyota Motor', 'NYSE', 'Consumer', 'JP', 192.70, -0.27, 0.3, 251, 8.9, 6.4, 2.6, '#eb0a1e'),
    S('BABA', 'Alibaba Group', 'NYSE', 'Consumer', 'CN', 168.35, 2.44, 7.8, 401, 19.6, 5.6, 1.1, '#ff6a00'),
    S('SHOP', 'Shopify Inc', 'NYSE', 'Technology', 'CA', 162.40, 1.86, 5.3, 211, 98.2, 26.1, 0, '#95bf47'),
    S('RY', 'Royal Bank of Canada', 'NYSE', 'Finance', 'CA', 148.25, 0.41, 1.1, 209, 15.1, 6.3, 3.2, '#005daa'),
    S('MELI', 'MercadoLibre', 'NASDAQ', 'Consumer', 'AR', 2104.60, -1.38, -2.7, 107, 51.7, 34.8, 0, '#ffe600'),
    S('PBR', 'Petrobras', 'NYSE', 'Energy', 'BR', 12.86, -1.53, -3.4, 83, 5.2, -6.1, 12.4, '#008542'),
    S('NU', 'Nu Holdings', 'NYSE', 'Finance', 'BR', 16.72, 2.95, 7.2, 81, 27.4, 41.3, 0, '#820ad1'),
    { s: 'SX5E', n: 'EURO STOXX 50', x: 'INDEX', c: 'indices', p: 5712.4, d: 0.22, w: 0.9, logo: '#1d4ed8', ext: true },
    { s: 'ES1', n: 'S&P 500 Futures', x: 'CME', c: 'indices', p: 7758.25, d: 0.11, w: 0.9, logo: '#ff7a1a', fut: true, ext: true },
    { s: 'YM1', n: 'Dow Jones Futures', x: 'CBOT', c: 'indices', p: 52341, d: 0.08, w: 0.4, logo: '#a1a1aa', fut: true, ext: true },
    { s: 'NQ1', n: 'Nasdaq 100 Futures', x: 'CME', c: 'indices', p: 29912.5, d: 0.19, w: 1.3, logo: '#0ea5e9', fut: true, ext: true },
    { s: 'HSI', n: 'Hang Seng', x: 'INDEX', c: 'indices', p: 25841.6, d: 0.94, w: 2.7, logo: '#dc2626', ext: true },
    { s: 'TSX', n: 'S&P/TSX Composite', x: 'INDEX', c: 'indices', p: 30184.2, d: 0.18, w: 0.6, logo: '#dc2626', ext: true },
    { s: 'IBOV', n: 'Bovespa', x: 'INDEX', c: 'indices', p: 142310, d: -0.42, w: 1.1, logo: '#16a34a', ext: true },
    { s: 'MXX', n: 'S&P/BMV IPC', x: 'INDEX', c: 'indices', p: 61240.5, d: 0.27, w: 0.8, logo: '#15803d', ext: true },
    { s: 'XJO', n: 'S&P/ASX 200', x: 'INDEX', c: 'indices', p: 8912.4, d: 0.33, w: 0.5, logo: '#1d4ed8', ext: true },
    { s: 'NZ50', n: 'NZX 50', x: 'INDEX', c: 'indices', p: 13185.7, d: -0.12, w: -0.3, logo: '#334155', ext: true },
    { s: 'J203', n: 'JSE All Share', x: 'INDEX', c: 'indices', p: 104870, d: 0.56, w: 1.4, logo: '#ca8a04', ext: true },
    { s: 'EGX30', n: 'EGX 30', x: 'INDEX', c: 'indices', p: 36920, d: 1.08, w: 2.3, logo: '#b91c1c', ext: true },
    { s: 'NGSE', n: 'NGX All-Share', x: 'INDEX', c: 'indices', p: 142650, d: 0.21, w: 0.9, logo: '#15803d', ext: true },
    { s: 'SENSEX', n: 'BSE Sensex', x: 'INDEX', c: 'indices', p: 83120, d: 0.44, w: 1.2, logo: '#ea580c', ext: true },
    { s: 'KOSPI', n: 'KOSPI', x: 'INDEX', c: 'indices', p: 3612.5, d: -0.38, w: 1.6, logo: '#2563eb', ext: true },
    { s: 'SSEC', n: 'Shanghai Composite', x: 'INDEX', c: 'indices', p: 3898.2, d: 0.15, w: 0.4, logo: '#dc2626', ext: true },
    { s: 'ADA', n: 'Cardano', x: 'CRYPTO', c: 'crypto', p: 0.6412, d: -0.84, w: -8.1, m: 23, vol: '$0.9B', logo: '#0033ad', ext: true },
    { s: 'AVAX', n: 'Avalanche', x: 'CRYPTO', c: 'crypto', p: 21.86, d: 3.10, w: -2.4, m: 9, vol: '$0.6B', logo: '#e84142', ext: true },
    { s: 'LINK', n: 'Chainlink', x: 'CRYPTO', c: 'crypto', p: 17.42, d: 1.60, w: -1.1, m: 11, vol: '$0.7B', logo: '#2a5ada', ext: true },
    { s: 'UNI', n: 'Uniswap', x: 'CRYPTO', c: 'crypto', p: 7.84, d: 2.20, w: 3.6, m: 5, vol: '$0.3B', logo: '#ff007a', defi: true, ext: true },
    { s: 'AAVE', n: 'Aave', x: 'CRYPTO', c: 'crypto', p: 241.30, d: 1.42, w: 4.4, m: 4, vol: '$0.4B', logo: '#b6509e', defi: true, ext: true },
    { s: 'USDT', n: 'Tether', x: 'CRYPTO', c: 'crypto', p: 1.0002, d: 0.01, w: 0.0, m: 182, vol: '$71.0B', logo: '#26a17b', stable: true, ext: true },
    { s: 'USDC', n: 'USD Coin', x: 'CRYPTO', c: 'crypto', p: 0.9999, d: 0.00, w: 0.0, m: 76, vol: '$9.8B', logo: '#2775ca', stable: true, ext: true },
    { s: 'EURGBP', n: 'Euro / British Pound', x: 'FX', c: 'currencies', p: 0.8698, d: 0.27, w: 0.7, logo: '#1d4ed8', ext: true },
    { s: 'EURJPY', n: 'Euro / Japanese Yen', x: 'FX', c: 'currencies', p: 176.75, d: 0.42, w: 1.3, logo: '#1d4ed8', minor: true, ext: true },
    { s: 'GBPJPY', n: 'British Pound / Japanese Yen', x: 'FX', c: 'currencies', p: 203.20, d: 0.15, w: 0.6, logo: '#ef4444', minor: true, ext: true },
    { s: 'EURCHF', n: 'Euro / Swiss Franc', x: 'FX', c: 'currencies', p: 0.9277, d: 0.03, w: 0.2, logo: '#1d4ed8', minor: true, ext: true },
    { s: 'USDTRY', n: 'US Dollar / Turkish Lira', x: 'FX', c: 'currencies', p: 42.31, d: 0.12, w: 0.5, logo: '#e30a17', exotic: true, ext: true },
    { s: 'USDMXN', n: 'US Dollar / Mexican Peso', x: 'FX', c: 'currencies', p: 18.46, d: -0.38, w: -0.9, logo: '#006847', exotic: true, ext: true },
    { s: 'USDZAR', n: 'US Dollar / South African Rand', x: 'FX', c: 'currencies', p: 17.38, d: -0.21, w: -0.4, logo: '#007a4d', exotic: true, ext: true },
    { s: 'PL', n: 'Platinum', x: 'NYMEX', c: 'commodities', p: 1612.40, d: 1.12, w: 3.3, unit: '/oz', group: 'Metals', logo: '#94a3b8', ext: true },
    { s: 'ZW', n: 'Wheat', x: 'CBOT', c: 'commodities', p: 5.18, d: -0.67, w: -1.5, unit: '/bu', group: 'Agriculture', logo: '#d97706', ext: true },
    { s: 'ZC', n: 'Corn', x: 'CBOT', c: 'commodities', p: 4.21, d: 0.48, w: 0.9, unit: '/bu', group: 'Agriculture', logo: '#facc15', ext: true },
    { s: 'KC', n: 'Coffee', x: 'ICE', c: 'commodities', p: 3.86, d: 2.05, w: 5.8, unit: '/lb', group: 'Agriculture', logo: '#78350f', ext: true },
    { s: 'ZS', n: 'Soybeans', x: 'CBOT', c: 'commodities', p: 10.42, d: 0.34, w: 1.2, unit: '/bu', group: 'Agriculture', logo: '#65a30d', ext: true },
    { s: 'UK10Y', n: 'UK 10-Year Gilt', x: 'BOND', c: 'bonds', p: 4.512, d: -0.3, w: -0.9, y: true, logo: '#64748b', ext: true },
    { s: 'IT10Y', n: 'Italy 10-Year BTP', x: 'BOND', c: 'bonds', p: 3.402, d: 0.4, w: 1.0, y: true, logo: '#64748b', ext: true },
    { s: 'USIG', n: 'US Investment-Grade Corporate', x: 'INDEX', c: 'bonds', p: 4.982, d: -0.5, w: -1.4, y: true, corp: true, logo: '#475569', ext: true },
    { s: 'USHY', n: 'US High-Yield Corporate', x: 'INDEX', c: 'bonds', p: 6.874, d: 0.8, w: 1.9, y: true, corp: true, logo: '#475569', ext: true },
    { s: 'VOO', n: 'Vanguard S&P 500 ETF', x: 'NYSE ARCA', c: 'funds', p: 709.80, d: -0.08, w: 0.9, aum: '$742B', fee: '0.03%', kind: 'ETF', logo: '#b91c1c', ext: true },
    { s: 'SCHD', n: 'Schwab US Dividend Equity', x: 'NYSE ARCA', c: 'funds', p: 28.42, d: 0.32, w: 0.6, aum: '$73B', fee: '0.06%', kind: 'Dividend ETF', logo: '#00a0df', ext: true },
    { s: 'ARKK', n: 'ARK Innovation ETF', x: 'NYSE ARCA', c: 'funds', p: 86.15, d: 2.74, w: 6.1, aum: '$8B', fee: '0.75%', kind: 'ETF', logo: '#111', ext: true },
    { s: 'TLT', n: 'iShares 20+ Year Treasury', x: 'NASDAQ', c: 'funds', p: 91.38, d: 0.41, w: 1.2, aum: '$58B', fee: '0.15%', kind: 'Bond ETF', logo: '#000', ext: true },
    { s: 'FXAIX', n: 'Fidelity 500 Index Fund', x: 'MUTUAL FUND', c: 'funds', p: 241.62, d: -0.08, w: 0.9, aum: '$728B', fee: '0.015%', kind: 'Index fund', logo: '#368727', ext: true },
    { s: 'VFIAX', n: 'Vanguard 500 Index Admiral', x: 'MUTUAL FUND', c: 'funds', p: 652.08, d: -0.08, w: 0.9, aum: '$1.6T', fee: '0.04%', kind: 'Index fund', logo: '#b91c1c', ext: true },
  );
  const grp = { WTI: 'Energy', BRENT: 'Energy', NG: 'Energy', XAU: 'Metals', XAG: 'Metals', HG: 'Metals' };
  assets.forEach(a => { if (grp[a.s]) a.group = grp[a.s]; if (a.c === 'stocks' && !a.country) a.country = 'US'; if (a.c === 'stocks' && a.g == null) a.g = +(a.w * 3 + 10).toFixed(1); if (a.c === 'stocks' && a.div == null) a.div = { AAPL: 0.4, MSFT: 0.6, JPM: 1.9, XOM: 3.4, V: 0.7, LLY: 0.6, AVGO: 1.2, GOOGL: 0.3, META: 0.3 }[a.s] || 0; });
  // Real prices (assets/quotes.js) replace the sample values wherever we have them
  const QD = window.QUOTES || {}, Q = QD.q || {};
  const vfmt = (v, usd) => (usd ? '$' : '') + (v >= 1e9 ? (v / 1e9).toFixed(1) + 'B' : v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v / 1e3).toFixed(0) + 'K');
  assets.forEach(a => {
    const q = Q[a.s];
    if (!q) { a.m1 = +(a.d * 3 + a.w).toFixed(2); a.spark = series(a.s, 48, a.p, a.m1); return; }
    const k = q.p / a.p;
    if (a.m != null) a.m = +(a.m * k).toFixed(a.m * k < 10 ? 1 : 0);
    if (a.pe != null) a.pe = +(a.pe * k).toFixed(1);
    Object.assign(a, { p: q.p, d: q.d, w: q.w, m1: q.m1, spark: q.sp.length > 2 ? q.sp : series(a.s, 48, q.p, q.m1), real: true, at: q.t, cur: q.cur, hi: q.hi, lo: q.lo, freq: q.freq, asof: q.asof });
    if (q.v) a.vol = vfmt(q.v, a.c === 'crypto');
  });
  const reitQ = r => { const q = Q[r.s]; if (q) Object.assign(r, { p: q.p, d: q.d, real: true }); };
  const updated = QD.updated ? new Date(QD.updated) : null;

  // Real chart history, loaded on demand: assets/hist/<SYM>.json (daily + weekly bars) and assets/intraday.json
  const cache = {};
  const getJSON = u => cache[u] || (cache[u] = fetch(u).then(r => r.ok ? r.json() : null).catch(() => null));
  const D = t => new Date(t * 1000);
  const fmtLab = { time: d => d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }), wd: d => d.toLocaleDateString('en-GB', { weekday: 'short' }), day: d => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }), mon: d => d.toLocaleDateString('en-GB', { month: 'short' }), yr: d => String(d.getFullYear()) };
  const labelsFor = (ts, kind, n = 5) => { if (ts.length < 2) return []; const out = []; for (let i = 0; i < n; i++) out.push(fmtLab[kind](D(ts[Math.round(i * (ts.length - 1) / (n - 1))]))); return out.filter((x, i, arr) => i === 0 || x !== arr[i - 1]); };
  // Returns { bars:[{o,h,l,c,v,t}], vals:[closes], labels, chg } for a range, or null when there's no real data
  async function history(sym, range) {
    if (!Q[sym]) return null;
    const a = bySym[sym], fromCloses = (ts, cs) => cs.map((c, i) => { const o = i ? cs[i - 1] : c; return { t: ts[i], o, h: Math.max(o, c), l: Math.min(o, c), c, v: 0 }; });
    let bars = null, kind = 'day';
    if (range === '1D' || range === '5D' || range === '1W') {
      const j = await getJSON('assets/intraday.json'), it = j && j.s[sym];
      if (it && range === '1D' && it.d1 && it.d1.c.length > 3) {
        const [t0, t1] = it.d1.t, n = it.d1.c.length, ts = it.d1.c.map((_, i) => t0 + (t1 - t0) * i / (n - 1));
        bars = fromCloses(ts, it.d1.c); kind = 'time';
      } else if (it && it.d5 && it.d5.length) {
        const ts = [], cs = []; it.d5.forEach(d => d.c.forEach((c, i) => { ts.push(d.t + i * 3600); cs.push(c); }));
        bars = fromCloses(ts, cs); kind = 'wd';
      }
    }
    if (!bars) {
      const h = await getJSON('assets/hist/' + sym + '.json'); if (!h) return null;
      const toBars = rows => rows.map(r => ({ t: r[0], o: r[1], h: r[2], l: r[3], c: r[4], v: r[5] }));
      const daily = toBars(h.daily), jan1 = new Date(new Date().getFullYear(), 0, 1) / 1000;
      if (h.freq === 'monthly') { bars = toBars(h.weekly).slice(range === '5Y' ? -60 : -12); kind = range === '5Y' ? 'yr' : 'mon'; }
      else if (range === '5Y') { bars = toBars(h.weekly); kind = 'yr'; }
      else if (range === 'YTD') { bars = daily.filter(b => b.t >= jan1); kind = 'mon'; }
      else { const n = { '1D': 2, '5D': 5, '1W': 5, '1M': 22, '3M': 64, '6M': 126, '1Y': 252 }[range] || 252; bars = daily.slice(-n - 1); kind = n <= 5 ? 'wd' : n <= 22 ? 'day' : 'mon'; }
    }
    if (!bars || bars.length < 2) return null;
    const last = bars[bars.length - 1]; last.c = a.p; last.h = Math.max(last.h, a.p); last.l = Math.min(last.l, a.p);
    const first = bars[0].c, chg = a.y ? +((last.c - first) * 100).toFixed(1) : +((last.c / first - 1) * 100).toFixed(2);
    return { bars, vals: bars.map(b => b.c), labels: labelsFor(bars.map(b => b.t), kind), chg };
  }
  const details = sym => Q[sym] ? getJSON('assets/hist/' + sym + '.json') : Promise.resolve(null);
  const intraday = () => getJSON('assets/intraday.json');
  const bySym = Object.fromEntries(assets.map(a => [a.s, a]));

  const categories = [
    { k: 'stocks', t: 'Stocks', d: 'US, European and global equities', page: 'stocks.html' },
    { k: 'indices', t: 'Indices', d: 'S&P 500, Nasdaq, DAX and futures', page: 'indices.html' },
    { k: 'crypto', t: 'Cryptocurrencies', d: 'Bitcoin, Ethereum, DeFi, stablecoins', page: 'crypto.html' },
    { k: 'currencies', t: 'Currencies', d: 'Major, minor and exotic pairs', page: 'currencies.html' },
    { k: 'commodities', t: 'Commodities', d: 'Energy, metals and agriculture', page: 'commodities.html' },
    { k: 'bonds', t: 'Bonds', d: 'Government yields, gilts, corporates', page: 'bonds.html' },
    { k: 'funds', t: 'Funds', d: 'ETFs, index and mutual funds', page: 'funds.html' },
  ];

  const news = [
    { id: 1, cat: 'Markets', tag: 'SPX', t: 'Stocks drift lower as inflation data keeps rate-cut bets in check', d: 'Treasury yields eased while tech led a quiet session ahead of next week’s earnings wave.', a: 'Léa Martin', time: '12 min ago', read: 4, img: 'spx' },
    { id: 2, cat: 'Crypto', tag: 'BTC', t: 'Bitcoin falls toward $80,000 as hot inflation print cools risk appetite', d: 'Spot ETF flows turned negative for a third day while funding rates reset across major venues.', a: 'Omar Haddad', time: '38 min ago', read: 5, img: 'btc' },
    { id: 3, cat: 'Earnings', tag: 'DELL', t: 'Dell drops 7% after Barclays questions the pace of AI server demand', d: 'The downgrade cites margin pressure as customers stretch purchase cycles into 2027.', a: 'Sofia Rossi', time: '1 h ago', read: 3, img: 'dell' },
    { id: 4, cat: 'Economy', tag: 'US10Y', t: 'What the Fed’s December meeting could mean for your mortgage', d: 'A plain-English guide to how policy rates filter through to borrowing costs.', a: 'Daniel Okafor', time: '2 h ago', read: 7, img: 'fed' },
    { id: 5, cat: 'Commodities', tag: 'XAU', t: 'Gold holds above $4,100 as central banks keep buying', d: 'Official-sector demand remains the steadiest pillar under the metal’s record run.', a: 'Léa Martin', time: '3 h ago', read: 4, img: 'gold' },
    { id: 6, cat: 'Stocks', tag: 'LLY', t: 'Eli Lilly climbs 3.5% on strong late-stage weight-loss pill results', d: 'Analysts see the oral drug widening the market well beyond injectable treatments.', a: 'Sofia Rossi', time: '4 h ago', read: 4, img: 'lly' },
    { id: 7, cat: 'Real Estate', tag: 'REITs', t: 'European office REITs rally as vacancy rates finally stabilise', d: 'Paris and Munich lead the recovery while secondary markets still lag.', a: 'Camille Dubois', time: '5 h ago', read: 6, img: 're' },
    { id: 8, cat: 'Currencies', tag: 'EURUSD', t: 'Euro edges up as ECB officials signal patience on further cuts', d: 'Traders pared bets on a December move after hawkish comments from Frankfurt.', a: 'Omar Haddad', time: '6 h ago', read: 3, img: 'eur' },
  ];

  const analysis = [
    { t: 'The AI capex cycle: who actually gets paid?', d: 'We map $600B of data-center spending across chips, power, cooling and real estate.', a: 'Investedia Research', role: 'Equity strategy', kind: 'Market outlook', read: 14, sentiment: 'Bullish', tag: 'NVDA' },
    { t: 'Why the yield curve is finally un-inverting', d: 'What a normal curve has meant for stocks, banks and housing in past cycles.', a: 'Daniel Okafor', role: 'Macro', kind: 'Market outlook', read: 9, sentiment: 'Neutral', tag: 'US10Y' },
    { t: 'Apple: services carry the story while iPhone stalls', d: 'Services now produce 45% of gross profit. We look at what that means for the valuation.', a: 'Sofia Rossi', role: 'Equities', kind: 'Stock analysis', read: 11, sentiment: 'Neutral', tag: 'AAPL' },
    { t: 'Bitcoin tests its 200-day average: what the chart says', d: 'Support, resistance and the levels traders are watching into November.', a: 'Omar Haddad', role: 'Digital assets', kind: 'Technical', read: 6, sentiment: 'Bearish', tag: 'BTC' },
    { t: 'Dividend aristocrats that still look cheap', d: 'Twelve companies with 25+ years of dividend growth trading below their 10-year average P/E.', a: 'Sofia Rossi', role: 'Income', kind: 'Fundamental', read: 8, sentiment: 'Bullish', tag: 'KO' },
    { t: 'Healthcare is the market’s quiet leader', d: 'Weight-loss drugs, cheaper valuations and defensive earnings make a strong sector case.', a: 'Investedia Research', role: 'Sector strategy', kind: 'Sector insight', read: 10, sentiment: 'Bullish', tag: 'LLY' },
    { t: 'Gold at $4,000: bubble or new floor?', d: 'Central-bank demand, real yields and the dollar, in three charts.', a: 'Léa Martin', role: 'Commodities', kind: 'Fundamental', read: 7, sentiment: 'Bullish', tag: 'XAU' },
    { t: 'Tesla’s chart is coiling. Which way does it break?', d: 'A tightening triangle, falling volume and two levels that matter.', a: 'Omar Haddad', role: 'Technical analysis', kind: 'Technical', read: 5, sentiment: 'Neutral', tag: 'TSLA' },
    { t: 'Energy stocks: priced for a glut that may not come', d: 'Why the sector’s low valuations already assume the worst for oil.', a: 'Daniel Okafor', role: 'Sector strategy', kind: 'Sector insight', read: 9, sentiment: 'Bearish', tag: 'XOM' },
  ];

  const calendar = [
    { day: 'Thu 16 Oct', time: '08:30', c: 'US', e: 'Initial Jobless Claims', imp: 2, act: '—', fc: '228K', prev: '224K' },
    { day: 'Thu 16 Oct', time: '08:30', c: 'US', e: 'Retail Sales MoM', imp: 3, act: '—', fc: '0.4%', prev: '0.6%' },
    { day: 'Thu 16 Oct', time: '11:00', c: 'EU', e: 'HICP Final YoY', imp: 2, act: '2.2%', fc: '2.2%', prev: '2.0%' },
    { day: 'Fri 17 Oct', time: '08:30', c: 'US', e: 'Housing Starts', imp: 2, act: '—', fc: '1.34M', prev: '1.31M' },
    { day: 'Fri 17 Oct', time: '10:00', c: 'US', e: 'UoM Consumer Sentiment', imp: 2, act: '—', fc: '55.1', prev: '55.0' },
    { day: 'Mon 20 Oct', time: '04:00', c: 'CN', e: 'GDP Growth Rate YoY', imp: 3, act: '—', fc: '4.8%', prev: '5.2%' },
    { day: 'Tue 21 Oct', time: '09:00', c: 'UK', e: 'Public Sector Net Borrowing', imp: 1, act: '—', fc: '£16.0B', prev: '£18.0B' },
    { day: 'Wed 22 Oct', time: '10:00', c: 'EU', e: 'Consumer Confidence Flash', imp: 1, act: '—', fc: '-14.9', prev: '-14.9' },
    { day: 'Thu 23 Oct', time: '14:15', c: 'EU', e: 'ECB Interest Rate Decision', imp: 3, act: '—', fc: '2.00%', prev: '2.00%' },
  ];
  const earnings = [
    { s: 'NFLX', n: 'Netflix', date: 'Tue 21 Oct', when: 'After close', eps: '6.97', rev: '$11.5B' },
    { s: 'TSLA', n: 'Tesla', date: 'Wed 22 Oct', when: 'After close', eps: '0.55', rev: '$26.4B' },
    { s: 'INTC', n: 'Intel', date: 'Thu 23 Oct', when: 'After close', eps: '0.01', rev: '$13.1B' },
    { s: 'MSFT', n: 'Microsoft', date: 'Wed 29 Oct', when: 'After close', eps: '3.66', rev: '$75.4B' },
    { s: 'META', n: 'Meta Platforms', date: 'Wed 29 Oct', when: 'After close', eps: '6.71', rev: '$49.4B' },
    { s: 'AAPL', n: 'Apple', date: 'Thu 30 Oct', when: 'After close', eps: '1.76', rev: '$101.2B' },
    { s: 'AMZN', n: 'Amazon', date: 'Thu 30 Oct', when: 'After close', eps: '1.57', rev: '$177.8B' },
  ];

  const realEstate = {
    cities: [
      { c: 'Paris', k: 'FR', price: 10420, yoy: -1.8, yld: 3.1, rent: 32.4 },
      { c: 'London', k: 'UK', price: 12890, yoy: 0.6, yld: 3.6, rent: 46.1 },
      { c: 'New York', k: 'US', price: 14210, yoy: 2.9, yld: 4.2, rent: 58.0 },
      { c: 'Dubai', k: 'AE', price: 5240, yoy: 11.4, yld: 6.8, rent: 29.7 },
      { c: 'Berlin', k: 'DE', price: 6980, yoy: 1.2, yld: 3.4, rent: 19.8 },
      { c: 'Lisbon', k: 'PT', price: 5880, yoy: 7.5, yld: 4.9, rent: 23.9 },
      { c: 'Madrid', k: 'ES', price: 5410, yoy: 9.8, yld: 5.1, rent: 22.6 },
      { c: 'Brussels', k: 'BE', price: 3960, yoy: 2.1, yld: 4.6, rent: 15.4 },
    ],
    reits: [
      { s: 'PLD', n: 'Prologis', t: 'Industrial', p: 121.40, d: 0.84, yld: 3.3 },
      { s: 'O', n: 'Realty Income', t: 'Retail', p: 58.92, d: 0.31, yld: 5.5 },
      { s: 'EQIX', n: 'Equinix', t: 'Data centers', p: 902.15, d: -0.42, yld: 2.0 },
      { s: 'AMT', n: 'American Tower', t: 'Towers', p: 196.70, d: -0.18, yld: 3.5 },
      { s: 'URW', n: 'Unibail-Rodamco-Westfield', t: 'Retail', p: 88.36, d: 1.92, yld: 5.9 },
      { s: 'VNA', n: 'Vonovia', t: 'Residential', p: 27.84, d: 1.05, yld: 4.3 },
    ],
  };

  // Candles: open/high/low/close/volume bars that end at `last`
  function ohlc(key, n, last, chg, vol = 0.014) {
    const closes = series(key + 'c', n, last, chg, vol), r = seeded(key + 'ohlc');
    return closes.map((c, i) => {
      const o = i ? closes[i - 1] * (1 + (r() - .5) * vol * .4) : c * (1 - chg / 100 / n);
      const hi = Math.max(o, c) * (1 + r() * vol * .7), lo = Math.min(o, c) * (1 - r() * vol * .7);
      return { o, h: hi, l: lo, c, v: (.55 + r() * .9) * (1 + Math.abs(c - o) / c / vol) };
    });
  }

  realEstate.reits.forEach(reitQ);
  // Real headlines (assets/news.js and assets/news/<SYM>.json, written by update_news.py) replace the sample stories
  const ago = ts => { const m = Math.max(1, Math.round((Date.now() / 1000 - ts) / 60)); return m < 60 ? m + ' min ago' : m < 1440 ? Math.round(m / 60) + 'h ago' : Math.round(m / 1440) + 'd ago'; };
  const toItem = (x, id) => ({ id, cat: x.cat, tag: (x.syms || [])[0] || '', syms: x.syms || [], t: x.t, d: x.d || '', a: x.src, time: ago(x.ts), ts: x.ts, read: null, img: id, url: x.u });
  if (window.NEWS && NEWS.items.length) news.splice(0, news.length, ...NEWS.items.map((x, i) => toItem(x, 'n' + i)));
  const newsFor = sym => getJSON('assets/news/' + sym + '.json').then(j => j && j.items.length ? j.items.map((x, i) => toItem(Object.assign({ syms: [sym] }, x), sym + i)) : news.filter(n => n.syms && n.syms.includes(sym)));
  return { assets, bySym, categories, news, analysis, calendar, earnings, realEstate, series, seeded, ohlc, history, details, intraday, updated, newsFor };
})();
