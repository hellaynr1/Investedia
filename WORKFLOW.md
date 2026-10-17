# Investedia weekly workflow (free models)

The owner runs this with free models through OmniRoute (`omni-research`, `omni-write`, `omni-code`). Claude reviews when available.
Every task: read AGENTS.md first, one step at a time, no background agents, work on a branch, never merge to main.

## The week at a glance (about 5–6 hours)

| Day | Block | Tool | Output |
|---|---|---|---|
| Mon (45 min) | **Research**: what moved markets last week + 1 competitor | `omni-research` | `research/YYYY-MM-DD-week.md` |
| Tue (60 min) | **Plan content**: 3 posts + 1 Reel + 1 newsletter from Monday's research | `omni-write` | `marketing/YYYY-MM-DD-plan.md` |
| Wed (60 min) | **Write**: captions, carousel slides, Reel script, newsletter draft | `omni-write` | `marketing/YYYY-MM-DD-*.md` |
| Thu (60 min) | **Design & post**: Canva with the brand kit; schedule in Instagram/TikTok | you + Canva | 3 posts scheduled |
| Fri (45 min) | **Site**: 1–2 small improvements from the to-do list | `omni-code` | a `preview/...` branch + screenshots |
| Sun (30 min) | **Review**: analytics dashboard (investedia.com/admin.html), Instagram insights; copy the summary into the Second Brain | you | 3 lessons + next week's focus |

## Content pillars (rotate)
1. **Market move explained**: "Why did NVIDIA drop 4% today?" (one chart, one sentence)
2. **Beginner basics**: ETFs, compound interest, what an index is
3. **POV / what-if**: "€100 a month in the S&P 500 since 2015" (use the site's calculator; label as past performance)
4. **Tool tour**: show one Investedia feature (world map, screener, watchlist) with a link
5. **Myth vs fact**: crypto risk, "get rich quick" claims

Every piece: a hook in the first line, plain language, a reason to send it to a friend, a link to investedia.com, and "For education, not financial advice."

## Prompts

**Monday research**
> Read AGENTS.md and WORKFLOW.md. Research: (1) the 5 biggest market moves of last week with the reason for each, (2) one competitor of Investedia [name], what they posted and what works. Reliable sources with links. One step at a time, no background agents. Save as `research/[date]-week.md` on branch `research/[date]`. End with 5 content ideas for young European beginners.

**Tuesday/Wednesday writing**
> Read AGENTS.md and WORKFLOW.md and `research/[date]-week.md`. Write: 3 Instagram carousels (6 slides each, max 20 words per slide), 1 Reel script (30 s, hook in the first 2 seconds), 10 alternative hooks, and a newsletter "3 market moves in 60 seconds". Plain language, no buy/sell advice, end with "For education, not financial advice." Save in `marketing/[date]-content.md` on branch `marketing/[date]`.

**Friday site task**
> Read AGENTS.md. Pick ONE small item from the to-do list (or: [task]). Work on a new branch `preview/[topic]`, run `python3 build.py`, take Playwright screenshots at 390px and 1440px, show them, do not merge.

## Do
- Give one small, clear task at a time.
- Check every fact and number free models give you (they can be wrong). Open the source links.
- Keep everything on branches; let Claude review before anything goes live.
- Reuse what works: when a post does well, ask for 5 variations of it.
- Copy the weekly summary from the analytics dashboard into the Second Brain.

## Don't
- Don't let free models touch accounts/login, emails, Supabase, the globe, or do redesigns.
- Don't merge to `main` or push to the live site yourself unless Claude or you checked the screenshots.
- Don't paste API keys or passwords into any chat or file.
- Don't post buy/sell recommendations, "guaranteed" returns or paid promotions without a clear label (Belgian/EU finfluencer rules).
- Don't publish AI text unedited: add your own voice and check it once.
- Don't run many agents at once: free models allow ~20 requests per minute.
