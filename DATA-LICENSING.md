# Data and content licensing register

Owner-facing register of every external data or content source in the repository, what it is used for, and what is still uncertain. Last reviewed 2026-10-28 from the code in this repository.

**Read this first**

- Nothing in this file is legal advice. It is a working register to hand to a lawyer.
- "Confirmed" means the terms were checked and written down. In this review **no provider's current terms were opened and verified**, so the column "Commercial display confirmed?" is **No** for all rows unless it says otherwise. That is deliberate: do not fill it in from memory.
- Investedia is still **pre-revenue**. Before any paid launch, every row marked "uncertain" needs a written licence or a lawyer's sign-off (see `LEGAL-TODO.md`).
- The site's own rules (from `AGENTS.md`): no copied article text, no publisher images, every story keeps its source name, link and time, AI summaries are labelled "AI-assisted", topic photos are labelled "Illustration".

## What Investedia stores from news sources

| Field kept | Source of the field | Shown to readers? |
|---|---|---|
| Headline | Written by Gemini from the publisher's headline (max 110 characters, rewritten neutrally) | Yes |
| Summary and "why it matters" | Written by Gemini from the headline and the article's **own short description** (meta description or feed description). The publisher's description is **not stored or shown**. | Yes, labelled AI-assisted |
| Source name, original URL, publication time | Feed or GDELT metadata | Yes |
| Image | Pixabay topic photo (licensed, credited). **No publisher images are used.** | Yes, labelled "Illustration" |

The original article text is never stored. Readers go to the publisher through the link.

## Register

Columns: **Source** · **Used for** · **Current usage in repo** · **Known or likely terms** · **Commercial display confirmed?** · **Attribution** · **Uncertainty**

### News and headlines

| Source | Used for | Current usage | Known or likely terms | Commercial display confirmed? | Attribution | Uncertainty |
|---|---|---|---|---|---|---|
| **GDELT DOC 2.0** (`api.gdeltproject.org`) | Global headline index (broad tier) | Headline, URL, domain, time per article; no key | GDELT publishes its index openly and asks for attribution. Terms for the headlines themselves are the publishers' terms. | No | Credit "GDELT-indexed" next to the source name | HIGH: confirms where a headline comes from, not that Investedia may show it commercially. Rate limit returns HTTP 429. |
| **Central bank and official RSS**: Federal Reserve (press, speeches, monetary), ECB, Bank of England, Bank of Japan, Bank of Canada, Bank of Korea, Sveriges Riksbank, Reserve Bank of Australia | Priority and broad tiers: official releases | Headline, link, time | Each institution has its own reuse terms; most publish press material for public reuse with attribution. **Not checked in this review.** | No | Name the institution (e.g. "ECB") | MEDIUM: verify each site's reuse page before commercial launch. |
| **US government**: Securities and Exchange Commission (`sec.gov`), Bureau of Economic Analysis (`bea.gov`), Energy Information Administration (`eia.gov`), Bureau of Labor Statistics (`bls.gov`, referenced in the code) | Priority and broad tiers | Headline, link, time | US federal works are generally not subject to US copyright, but this does not cover third-party content in them and is not a licence statement. **Not checked.** | No | Name the agency | MEDIUM. |
| **Publisher business RSS**: BBC News, The Guardian, The New York Times, MarketWatch (Dow Jones feed), South China Morning Post, The Straits Times, ABC News Australia, CoinDesk, OilPrice.com, Investing.com, Cointelegraph (in `update_news.py`) | Broad tier (MarketWatch also priority) | Headline, link, time, publisher name; their description is read only as input for the summary | RSS feeds are often offered for personal or syndication use. Several publishers prohibit scraping or commercial reuse in their terms. **Not checked for any publisher.** | **No** | Name the publisher on every story | HIGH. Commercial use of headlines from these publishers needs a licence or an explicit permission. |
| **Regional publisher RSS** (about 34 feeds: Moneyweb, Nairametrics, BusinessDay, Daily News Egypt, AllAfrica, TechCabal, IOL, Infobae, Clarín, La Nación, Exame, Brazil Journal, Portafolio, El Comercio, Daily Sabah, Hürriyet Daily News and others) | Broad tier, regions | As above | As above; several are small publishers with no published reuse terms. | **No** | Name the publisher | HIGH. |
| **Banco de la República (Colombia) RSS** | Broad tier | As above | Central bank: check its reuse page | No | Name the bank | MEDIUM. |
| **Google News RSS** (`news.google.com`) | Asset-level headlines in `update_news.py` (asset pages) | Headline, link, source, time | Google's RSS is a public endpoint without published reuse terms for this use. | **No** | Name the source | HIGH. Used for asset pages, not the globe. |
| **Yahoo Finance RSS** (`feeds` in `update_news.py`) | Asset-level headlines | As above | Yahoo's terms restrict commercial use. The owner has already noted: "Yahoo's free feed is not for commercial use" (`AGENTS.md`). | **No** | Name the source | HIGH. |

### Prices and market data

| Source | Used for | Current usage | Known or likely terms | Commercial display confirmed? | Attribution | Uncertainty |
|---|---|---|---|---|---|---|
| **Yahoo Finance chart API** (`query1.finance.yahoo.com`, seven references in code) | Stock, index, currency, commodity and bond prices and history (`update_market.py`, `update_globe.py`, `update_news_prices.py`, `update_prices.py`) | Prices shown on the Markets, Globe and asset pages; delayed 15–30 minutes | Unofficial endpoint; not licensed for commercial use. Owner's note in `AGENTS.md`. | **No** | "Delayed" label on every price | HIGH. Must move to a licensed provider before any revenue. Do not call these prices live. |
| **Coinbase public market data** (`api.coinbase.com`) via Cloudflare Worker (`workers/live/index.js`) | Crypto prices shown as LIVE | Top 100 USD spot pairs, refreshed every ~3 seconds at the relay | Coinbase's public market data terms apply. Not checked here. | **No** | Coinbase named as the source | MEDIUM. Confirm the terms before the "LIVE" label is commercial. |
| **ForexFactory calendar mirror** (`nfs.faireconomy.media`) | Economic calendar events (`calendar_official.py`, `calendar_fred.py`, `update_calendar.py`) | Events and times on the Calendar page | An unofficial mirror of ForexFactory's calendar. ForexFactory's terms restrict reuse. | **No** | Name the source | HIGH. |
| **FRED** (Federal Reserve Bank of St. Louis, `api.stlouisfed.org`) | US economic series for the calendar (`calendar_fred.py`) | Series values and dates | FRED requires an API key. Each series may carry a third-party licence. | **No** (per series unknown) | "Source: FRED, Federal Reserve Bank of St. Louis" | MEDIUM. Check series-level notes before commercial use. |
| **World Bank** (`api.worldbank.org`, `data.worldbank.org`) | Country GDP, growth, inflation, jobs (`update_economy.py`) | Country panels on the Globe | World Bank Open Data is usually published under CC BY 4.0. **Not checked in this session**; verify the current page. | Likely yes, to verify | Name the World Bank, link the licence | LOW–MEDIUM. |
| **Nasdaq earnings calendar** | Earnings dates (named in `AGENTS.md`; endpoint not located in this review) | Earnings on the calendar | Nasdaq's data terms restrict redistribution. | **No** | Name the source | HIGH. Endpoint to be located and documented. |
| **Natural Earth country outlines** (`countries-50m.json`, `countries-110m.json`) | Globe shapes | Drawn on the globe | Natural Earth data is in the public domain. File origin to be confirmed with the build history. | Likely yes, to verify | Credit Natural Earth | LOW. |

### AI, images and other services

| Source | Used for | Current usage | Known or likely terms | Commercial display confirmed? | Attribution | Uncertainty |
|---|---|---|---|---|---|---|
| **Google Gemini API** (`generativelanguage.googleapis.com`) | Story selection, summaries, "why it matters", impact analysis | Every robot run; API key in GitHub secrets | Google's free tier can use submitted content to improve its products; paid-tier terms differ. **Not checked.** | **No** | Label output "AI-assisted" (done) | HIGH for privacy: input is headlines and short descriptions only, never private user data. Verify tier terms before launch. |
| **Pixabay** (`pixabay.com`) | Topic photos (illustrations) | Downloaded once per topic, credited, labelled "Illustration" | Pixabay Content License: free use including commercial, no attribution required, but no standalone resale and no use that implies a real person or event. The repo keeps credits. The licence page is linked in the code. | Likely yes under Pixabay's published licence summary. **Not re-verified in this review**; re-check before launch | Credit photographer + "Pixabay", label "Illustration" | LOW–MEDIUM. Photos are topic illustrations, never shown as news photos. |
| **Brandfetch CDN** (`cdn.brandfetch.io`) | Company logos on the Globe | Logos loaded in the browser | Logos are trademarks. Brandfetch's terms restrict some uses. Client ID is public in `tools/globe-news/page.html`. | **No** | Nominative use only | MEDIUM. |
| **Supabase** (`lfjyoeusblhfpmgwbrhj.supabase.co`) | Accounts, watchlists, analytics | Browser uses the public (publishable) key only | Service. Terms: not a content licence. Service-role key is **not** in the repo (checked). | Not applicable | Not applicable | LOW. |
| **Google Fonts** (`fonts.googleapis.com`) and **Inter** font files in `tools/share/` | Typefaces | Page text | Inter is distributed with its licence file (`tools/share/LICENSE.txt`); check that file matches the version in use. Google Fonts terms for web use: to verify. | To verify | Licence file kept | LOW. |
| **jsDelivr** (`cdn.jsdelivr.net`) | Libraries loaded in the browser | Not fully inventoried in this review | Each library has its own licence. | To verify | Per library | MEDIUM: inventory the exact libraries. |
| **axe-core 4.10.3** (`tests/vendor/`) | Accessibility tests only | Not shipped to readers | Believed to be Mozilla Public License 2.0 (upstream project); check the bundled file | Not applicable | Keep licence notice | LOW. |

## Things found that need your decision

1. **Publisher headlines in the broad tier.** Several publisher RSS feeds are used without a confirmed licence. Options: (a) keep them with a licence request to each publisher, (b) drop the publishers and keep official sources plus GDELT, or (c) buy a licensed news feed later. This is a commercial and legal choice, so it is yours to make.
2. **Publisher descriptions are read by the editor step.** The robot reads each article's own short description (or the page's meta description, up to 300 KB) to write our summary. The description is never stored or shown, but the page fetch is a form of automated reading of publisher pages. Consider removing the page fetch and relying only on feed descriptions.
3. **Yahoo prices and Yahoo/Google headlines.** Already flagged in `AGENTS.md`. Not for commercial use.
4. **ForexFactory mirror.** Unofficial; should be replaced by a licensed calendar before launch.
5. **Gemini free tier.** Check whether using the free tier with headlines is acceptable for a commercial product. A paid tier would need your approval (cost).

## What I did not do

- I did not open or verify any provider's terms page. Each "Not checked" above is a task for you or a lawyer.
- I did not remove any source, even where the terms are doubtful, because the owner asked to flag rather than remove unless clearly unsafe.
- I did not change any licensing or branding claim on the site.
