# Investedia AI system — OmniRoute setup

This guide connects your own **OmniRoute** gateway to the Investedia GitHub repo, so that:

1. **The site writes AI notes by itself.** A "Market brief" appears on the homepage and News page, and a "Why it's moving" card appears on asset pages. They are written from the real prices and headlines the site already collects, and are labelled *AI-generated · Not investment advice*.
2. **You can hand coding tasks to other AIs from your phone.** You open a GitHub issue with the label `ai-task`, an open-source coding agent (Aider) does the work through OmniRoute, and it opens a pull request for you to review.
3. **You can still use Claude (me) from your phone** in the Claude app, as you do now. I work on the same repo and can review the other AIs' pull requests.

The repo side is already built and live (`scripts/ai_brief.py`, `.github/workflows/ai-task.yml` and the AI cards on the site). Until you finish the steps below, everything AI simply stays hidden, so nothing breaks.

Total time is about 45–60 minutes. It costs $0 on Oracle Cloud's free tier, or about $5 a month on a small VPS.

---

## 0. What you need
- A computer for the first setup (a laptop is easiest; after that, the phone is enough).
- Your domain login (where `investedia.com` DNS is managed).
- Free accounts for at least one AI provider: **Google AI Studio** (Gemini), **Groq** or **OpenRouter**. Having two or three is better, so OmniRoute can switch when one hits its free limit.

> Only use the official project: **github.com/diegosouzapw/OmniRoute**. There is a different, unrelated project also called OmniRoute (`v0l/OmniRoute`).

---

## 1. Get an always-on server

OmniRoute has to run 24/7 so GitHub can reach it. Your own laptop can't do this, because it sleeps.

**Option A: free (Oracle Cloud Always Free)**
1. Sign up at cloud.oracle.com. A card is asked for verification only; Always Free resources are not charged.
2. Create a VM instance: **Ubuntu 24.04**, shape **VM.Standard.A1.Flex** (ARM), 2 OCPU / 8 GB RAM is plenty. Download the SSH key it gives you.
3. Networking → your VCN → Security List → add **Ingress rules** for TCP **80** and **443** from `0.0.0.0/0`.
4. Note the server's **public IP**.

**Option B: about $5 a month (Hetzner, DigitalOcean, Vultr…)**
Create an Ubuntu 24.04 server with 2 GB RAM or more and note its public IP. Ports 80 and 443 are usually open already.

Connect from your computer:
```bash
ssh -i path/to/key ubuntu@YOUR_SERVER_IP        # Oracle (user "ubuntu")
ssh root@YOUR_SERVER_IP                          # most VPS providers
```

---

## 2. Point `ai.investedia.com` at the server

At your DNS provider, add one record:

| Type | Name | Value | TTL |
|---|---|---|---|
| A | `ai` | YOUR_SERVER_IP | Auto |

This doesn't touch the main site; GitHub Pages keeps serving `investedia.com`.

---

## 3. Install Docker and OmniRoute

Run on the server:
```bash
# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker

# Oracle Ubuntu images also block 80/443 in the server's own firewall. Skip on other VPS.
sudo iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
sudo apt-get install -y iptables-persistent && sudo netfilter-persistent save

# OmniRoute
git clone https://github.com/diegosouzapw/OmniRoute.git && cd OmniRoute
cp .env.selfhost.example .env
nano .env
```

In `.env`, set these lines and leave the rest as they are:
```env
APP_BIND_HOST=127.0.0.1                        # only reachable through HTTPS below
REQUIRE_API_KEY=true                           # IMPORTANT: no key, no access
INITIAL_PASSWORD=choose-a-long-unique-password # your dashboard login
NEXT_PUBLIC_BASE_URL=https://ai.investedia.com
OMNIROUTE_MEMORY_MB=2048
```
Save with Ctrl+O, Enter, Ctrl+X. **Never put this `.env` file in GitHub.**

Start it:
```bash
docker compose -f docker-compose.selfhost.yml up -d
docker compose -f docker-compose.selfhost.yml ps      # should show omniroute + redis "running"
curl -s localhost:20128 >/dev/null && echo OK
```
If the Docker image won't start on the ARM server, use the npm install instead: `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y nodejs && sudo npm install -g omniroute && omniroute`. Then keep it running with `pm2` or a systemd service.

---

## 4. HTTPS with Caddy (automatic certificate)

```bash
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update && sudo apt-get install -y caddy

sudo tee /etc/caddy/Caddyfile >/dev/null <<'EOF'
ai.investedia.com {
    reverse_proxy 127.0.0.1:20128
}
EOF
sudo systemctl reload caddy
```
Wait a minute, then open **https://ai.investedia.com** on your phone. You should see the OmniRoute login page with a padlock. Log in with your `INITIAL_PASSWORD`.

---

## 5. Connect AI providers (in the dashboard)

Get free API keys:
- **Gemini:** aistudio.google.com → Get API key
- **Groq:** console.groq.com → API Keys
- **OpenRouter:** openrouter.ai → Keys (use models ending in `:free`)

In the OmniRoute dashboard, go to **Providers**, add each key, and press test. OmniRoute stores the keys encrypted.

Free tiers have rate limits, and some providers' terms don't allow reselling or relaying to other people. This setup is for your own projects only, so that is fine. Don't open your gateway to the public.

---

## 6. Create the key GitHub will use

In the dashboard, go to **Endpoints / API keys**, create a key named `github-investedia`, and copy it. You only see it once.

Test it from any computer:
```bash
curl https://ai.investedia.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_OMNIROUTE_KEY" -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Say hi in 3 words"}]}'
```
A JSON answer means the gateway works.

---

## 7. Give GitHub the secrets (works from the phone)

Go to github.com/hellaynr1/Investedia → **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|---|---|
| `OMNIROUTE_URL` | `https://ai.investedia.com` (no `/v1`, no slash at the end) |
| `OMNIROUTE_KEY` | the key from step 6 |

Optional, under the **Variables** tab: `OMNIROUTE_CODE_MODEL`. It is the model the coding agent uses, default `auto/coding`.

Then go to **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**, tick **Allow GitHub Actions to create and approve pull requests**, and press Save.

Finally, under **Issues → Labels → New label**, create a label named `ai-task`.

---

## 8. Turn it on and check

- **AI notes on the site:** go to **Actions → Update market data and news → Run workflow**. After about 2 minutes the Market brief appears on the homepage and News page, and "Why it's moving" appears on the biggest movers' pages. From then on it refreshes every 2 hours on weekdays during market hours.
- **AI coding task from the phone:** in the GitHub app, go to Issues → New → **AI task**. Write what should change, e.g. *"On the calculator page, make the result number bigger on phone"*, and submit. The label is added automatically. In about 5–15 minutes, a pull request appears and is linked in the issue. Open **Files changed**, then **Merge** if it's good, or close it if not. Only you (the repo owner) can start these tasks, and nothing goes live without your merge.

---

## 9. Using everything from your phone

| What | Where |
|---|---|
| Talk to Claude, give me tasks, see what I change | Claude app → Code (this session or a new one on the Investedia repo) |
| Give tasks to the other AIs, review and merge their PRs | GitHub app → Issues / Pull requests |
| See AI usage, costs, providers, switch models | https://ai.investedia.com (add it to your home screen) |
| See the result | investedia.com |

How the AIs work together: every AI (me included) works on the same GitHub repo, and every change arrives as a commit or pull request. You can ask me in the Claude app to "review the open AI pull requests", and I'll check them, fix problems and tell you what is safe to merge. Later you can connect more agents (OpenHands, Cline, Continue, other tools that accept an OpenAI-compatible URL) to the same `https://ai.investedia.com/v1` endpoint with their own keys.

Note: I (Claude) don't run through OmniRoute. I run on Anthropic's servers in the Claude app, which you already have. OmniRoute is for the *other* AIs and for the site's AI features.

---

## 10. Safety checklist
- `REQUIRE_API_KEY=true` and a strong `INITIAL_PASSWORD` are set before the domain is live.
- `.env` and keys are never committed. `.env` is in `.gitignore`, and keys live only in GitHub Secrets and the OmniRoute dashboard.
- Each tool gets its own OmniRoute key, so you can revoke one without breaking the others.
- Update every month or so: `cd OmniRoute && git pull && docker compose -f docker-compose.selfhost.yml up -d --pull always`.
- The gateway sees every prompt and answer that goes through it. Don't send passwords or private documents through it.
- AI text on the site is always labelled *AI-generated · Not investment advice*, and is written only from real data the site already shows.

## If something doesn't work
| Problem | Fix |
|---|---|
| https://ai.investedia.com doesn't load | DNS can take up to an hour. Check that the A record shows the right IP, and that ports 80/443 are open (step 1.3 and the iptables lines). `sudo journalctl -u caddy -n 50` shows the reason. |
| Dashboard password unknown | `docker logs omniroute 2>&1 \| grep -i password` |
| GitHub run says "OmniRoute not configured" | The secret names must be exactly `OMNIROUTE_URL` and `OMNIROUTE_KEY`. |
| `401` errors | Wrong key, or the key was deleted. Create a new one (step 6). |
| `429` errors | Free limit reached. Add another provider in step 5. |
| AI task makes no PR | Check the step 7 permissions, and that the label is exactly `ai-task`. |
