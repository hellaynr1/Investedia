# Setup guide: free data keys + Cloudflare (about 45 minutes, no cost)

Do these on your computer. **Never paste a key into a chat, an email or a file in the repo.** Keys go only into GitHub Secrets
or Cloudflare secrets as described below. When you're done, just tell Claude "keys are in" — Claude never needs to see them.

---

## Part 1 — Finnhub (earnings surprises, analyst upgrades/downgrades)

1. Go to **https://finnhub.io** → **Get free API key** (top right).
2. Sign up with your email (or Google). Confirm the email if asked.
3. You land on the **Dashboard**. Your key is shown at the top under **API Key** (a string like `c1abc...`). Click **copy**.
4. Free plan limits: 60 calls per minute. That is plenty.

**Put it in GitHub:**
1. Open **https://github.com/hellaynr1/Investedia/settings/secrets/actions**
2. Click **New repository secret**.
3. Name: `FINNHUB_KEY` (exactly like this) — Secret: paste the key → **Add secret**.

## Part 2 — Alpha Vantage (earnings estimates and surprise history)

1. Go to **https://www.alphavantage.co/support/#api-key**
2. Fill in: "Which of the following best describes you?" → **Investor** (or Software developer); organisation: `Investedia`; your email.
3. Click **GET FREE API KEY**. The key appears on the same page (a string like `ABCD1234EFGH5678`). Copy it.
4. Free plan limit: 25 calls per day (we use it only for a small daily top-up).

**Put it in GitHub:** same page as above → **New repository secret** → Name: `ALPHAVANTAGE_KEY` → paste → **Add secret**.

Check: on https://github.com/hellaynr1/Investedia/settings/secrets/actions you should now see `FINNHUB_KEY` and
`ALPHAVANTAGE_KEY` in the list (values are hidden — that's correct).

---

## Part 3 — Cloudflare (faster news and faster calls)

What this gives you: GitHub's timer is unreliable (runs often start 10–40 minutes late). Cloudflare will (a) serve the newest
news to the site within seconds, and (b) act as a precise alarm clock that wakes the news robot and the v5 engine every few
minutes. All on the free plan.

### 3.1 Account and tools (once)
1. Create a free account at **https://dash.cloudflare.com/sign-up**.
2. Install **Node.js** (LTS) from **https://nodejs.org** if you don't have it. Check in a terminal: `node -v` shows a version.
3. Get the code: `git clone https://github.com/hellaynr1/Investedia.git` then `cd Investedia/workers/live`
   (if you already have it: `cd Investedia && git pull origin main && cd workers/live`).
4. Run `npm install` then `npx wrangler login` — a browser window opens; click **Allow**.

### 3.2 Deploy the Worker
1. In `Investedia/workers/live` run: `npx wrangler deploy`
2. It prints a URL like `https://investedia-live.<your-name>.workers.dev`. **Copy it.**
3. Test: open `<that URL>/v1/status` in your browser. You should see JSON text. That means it works.

### 3.3 The news ingest password (lets the robot send news to the Worker)
1. Make a long random password. On Mac/Linux: `openssl rand -hex 32` (Windows: use any password manager to generate 40+ characters).
2. In `workers/live` run `npx wrangler secret put INGEST_TOKEN` and paste the password when asked.
3. In GitHub → **Settings → Secrets and variables → Actions**:
   - **Secrets** tab → New repository secret → Name `NEWS_INGEST_TOKEN` → paste the **same** password.
   - **Variables** tab → New repository variable → Name `WORKER_URL` → value: the Worker URL from 3.2 (no slash at the end).

### 3.4 The "alarm clock" token (lets Cloudflare start the GitHub robots on time)
1. Go to **https://github.com/settings/personal-access-tokens/new** (fine-grained token).
2. Token name: `investedia-cloudflare-alarm`. Expiration: 1 year.
3. Repository access: **Only select repositories** → `hellaynr1/Investedia`.
4. Permissions → Repository permissions → **Actions: Read and write**. Leave everything else on "No access".
5. **Generate token** → copy it (starts with `github_pat_`).
6. In `workers/live` run `npx wrangler secret put GITHUB_DISPATCH_TOKEN` and paste it.
   (Claude will add the small alarm code to the Worker; until then this token is simply stored and unused.)

### 3.5 Optional: your own address
Cloudflare dashboard → **Workers & Pages** → `investedia-live` → **Settings → Domains & Routes → Add → Custom domain** →
`live.investedia.com`. This needs `investedia.com` added to Cloudflare first (dashboard → **Add a domain**, follow the steps;
your site stays on GitHub Pages). If you skip this, the `workers.dev` address works fine.

---

## When you're done, tell Claude:
"keys are in" (Finnhub + Alpha Vantage) and "cloudflare is set" (+ whether you did 3.5).

Claude will then: switch on the surprise data in the engine, scoring against the sector (if you approve), the Cloudflare alarm
clock (every 5 minutes for news, every 10 for the engine), and the site reading fresh news from the Worker.

## If something goes wrong
- `wrangler: command not found` → use `npx wrangler ...` (with npx) as written above.
- `Authentication error` on deploy → run `npx wrangler login` again.
- A key was pasted somewhere public by mistake → delete it on the provider's site (Finnhub dashboard / Alpha Vantage: request a new
  one / GitHub: Settings → Developer settings → tokens → delete) and make a new one.
