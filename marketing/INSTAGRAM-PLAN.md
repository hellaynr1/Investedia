# Investedia — Instagram launch kit

Every file is in `marketing/out/`. Feed posts are 1080×1350 (4:5), stories and reels 1080×1920, highlight covers 1080×1920 (icon centred for the circle crop), profile picture 1080×1080.

## Profile
- **Profile picture:** `avatar.png`
- **Name:** Investedia
- **Category:** Financial service
- **Bio:**
  ```
  Markets, made clear.
  Live prices · Charts · News · Free tools
  Not financial advice.
  ```
- **Link:** investedia.com

## Highlights (left to right)
| Highlight | Cover | Stories inside |
|---|---|---|
| Start | `cv_start.png` | `v_logo.mp4` → `s_start1.png` → `s_start2.png` → `s_start3.png` |
| Markets | `cv_markets.png` | `v_markets.mp4` → `s_mk2.png` |
| Tools | `cv_tools.png` | `s_tools1.png` |
| Learn | `cv_learn.png` | `s_learn1.png` |
| News | `cv_news.png` | `s_news1.png` |
| App | `cv_app.png` | `v_app.mp4` |

How to set a cover: post the cover image as a story, add it to the highlight, then Edit highlight → Edit cover → choose it.

## Posting order (oldest first, so the grid reads well)
Post one per day, or all at once for launch day.

1. `p1.png`
   > Introducing Investedia. Markets, tools and learning in one clear place. Free at investedia.com
2. `p2.png`
   > Stocks, indices, crypto, currencies, commodities, bonds and funds. 240+ assets across 6 continents, in one clear view.
3. `p3.png`
   > Real prices, updated through the day. Crypto and currencies move live on the site.
4. `reel_intro.mp4` (Reel)
   > This is Investedia. Every market, in one clear place. 📈 investedia.com
5. Carousel: `c1.png` `c2.png` `c3.png` `c4.png` `c5.png`
   > What is Investedia? Swipe to see how it works. Free, on any phone, no sign-up.
6. `p4.png`
   > The whole currency market at a glance. Tap any square on the site to see what moved and why.
7. `p5.png`
   > Pick a region and see what's rising, from Europe and Asia to the Americas, Africa and the Middle East.
8. `p6.png`
   > Just starting or years in, there's a place for you here.
9. `p7.png`
   > Free tools that answer real money questions: what if I had invested, compound interest, rent vs. buy and a stock screener.
10. `p8.png`
    > Learn as you go. Short lessons and a full glossary, in plain English.
11. `p9.png`
    > Put Investedia on your home screen. Open investedia.com, tap Share, then Add to Home Screen. No App Store needed.

**Hashtags (pick 5–8, at the end of the caption):** #investing #stockmarket #finance #crypto #forex #personalfinance #financialliteracy #investingforbeginners #markets #trading

**Disclaimer to keep in captions where prices or tools appear:** Information and education only. Not investment advice.

Note: post 3, the markets story and the news story show real prices and headlines from 16 October. Re-render before posting on a later day: `node render.mjs` (images) and `node video.mjs v_markets` (video) inside `marketing/`, after refreshing `data.js`.

## POV reels (marketing/pov/)
Real data: $100 invested at the start of every month, values at real daily closing prices (dividends included via adjusted prices), up to 16 October 2026.

| File | Title | Put in | Worth today |
|---|---|---|---|
| pov_amd.mp4 | POV: You invested $100 in AMD monthly since 2016 | $13,000 | $319,482 |
| pov_nvidia.mp4 | …NVIDIA monthly since 2016 | $13,000 | $492,326 |
| pov_bitcoin.mp4 | …Bitcoin monthly since 2016 | $13,000 | $289,502 |
| pov_eli_lilly.mp4 | …Eli Lilly monthly since 2016 | $13,000 | $109,324 |
| pov_tsmc.mp4 | …TSMC monthly since 2016 | $13,000 | $101,486 |
| pov_apple.mp4 | …Apple monthly since 2014 | $15,400 | $101,662 |

Caption idea: "$100 a month into [asset] since [year]. Try any stock with the free POV calculator at investedia.com 📈 Not financial advice. Past performance doesn't guarantee future results."
