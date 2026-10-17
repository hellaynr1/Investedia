# Investedia research system

Persistent competitor intelligence. Claude reads this folder at the start of every research cycle and writes back to it at the end. Update existing files; do not create duplicates.

| File | Purpose |
|---|---|
| `STRATEGIST.md` | Standing instructions and rules for the research agent |
| `competitors/INDEX.md` | Every tracked competitor, handles, last-researched date |
| `competitors/<slug>.md` | One profile per competitor (evidence vs interpretation) |
| `LOG.md` | Dated log of each research cycle and what was found |
| `experiments/EXPERIMENTS.md` | Hypotheses, metrics, results, rejected approaches |
| `BACKLOG.md` | Ranked next research tasks |
| `CAPABILITIES.md` | What tools actually work from each environment (no guessing) |
