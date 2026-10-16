"""Write short AI market notes for the site through your OmniRoute gateway.

  python3 scripts/ai_brief.py

Needs three environment variables (GitHub repository secrets in the workflow):
  OMNIROUTE_URL    e.g. https://ai.investedia.com      (no trailing /v1)
  OMNIROUTE_KEY    an API key created in the OmniRoute dashboard
  OMNIROUTE_MODEL  optional, default "auto" (OmniRoute picks a free model that works)

Reads real prices (assets/quotes.js) and real headlines (assets/news.js), asks the model for
a market brief and one-line "why it's moving" notes, and writes assets/ai.json (+ docs copy).
Without the variables it does nothing, so the site keeps working.
"""
import json, os, re, shutil, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL, KEY, MODEL = os.environ.get("OMNIROUTE_URL", "").rstrip("/"), os.environ.get("OMNIROUTE_KEY", ""), os.environ.get("OMNIROUTE_MODEL") or "auto"


def load(name):
    t = open(os.path.join(ROOT, "assets", name)).read()
    return json.loads(t[t.index("{"):t.rindex("}") + 1])


def ask(prompt):
    body = json.dumps({"model": MODEL, "temperature": 0.3, "messages": [
        {"role": "system", "content": "You write short, neutral market notes for a finance education website. Only use the facts given. Never give advice, predictions or price targets. Plain English, no hype, no emojis."},
        {"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(URL + "/v1/chat/completions", data=body, headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    for i in range(3):
        try:
            return json.load(urllib.request.urlopen(req, timeout=90))["choices"][0]["message"]["content"]
        except Exception as e:
            if i == 2:
                raise
            time.sleep(5 * (i + 1))


def main():
    if not URL or not KEY:
        print("OmniRoute not configured (OMNIROUTE_URL / OMNIROUTE_KEY); skipping AI notes.")
        return
    q, news = load("quotes.js")["q"], load("news.js")["items"]
    big = sorted([(s, v) for s, v in q.items() if isinstance(v.get("d"), (int, float)) and not s.endswith("10Y")], key=lambda x: -abs(x[1]["d"]))[:8]
    heads = [f"- [{n.get('cat')}] {n['t']} ({n['src']})" + (f" tags: {','.join(n.get('syms', []))}" if n.get('syms') else "") for n in news[:30]]
    movers = [f"- {s}: {v['d']:+.2f}% today, {v.get('w', 0):+.2f}% this week" for s, v in big]
    prompt = ("Today's biggest moves:\n" + "\n".join(movers) + "\n\nLatest headlines:\n" + "\n".join(heads) +
              "\n\nReturn ONLY JSON with this shape: {\"brief\": [3 to 5 short sentences summarising the market today], "
              "\"why\": {\"SYMBOL\": \"one sentence on what the headlines say about this move, or 'No clear news behind this move.'\"}} "
              "Include a 'why' entry for each symbol in the moves list.")
    raw = ask(prompt)
    m = re.search(r"\{.*\}", raw, re.S)
    data = json.loads(m.group(0)) if m else None
    if not data or not isinstance(data.get("brief"), list):
        sys.exit("The model did not return usable JSON; keeping the previous notes.")
    out = {"updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "model": MODEL,
           "brief": [str(x)[:300] for x in data["brief"][:5]],
           "why": {s: str(t)[:240] for s, t in (data.get("why") or {}).items() if s in q}}
    path = os.path.join(ROOT, "assets", "ai.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    if os.path.isdir(os.path.join(ROOT, "docs", "assets")):
        shutil.copy2(path, os.path.join(ROOT, "docs", "assets", "ai.json"))
    print(f"AI notes written: {len(out['brief'])} brief lines, {len(out['why'])} movers")


if __name__ == "__main__":
    main()
