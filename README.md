# 📓 Captain's Log

**Your daily engineering journal, automated.**

Captain's Log scrapes your GitHub commits and uses AI (via [OpenRouter](https://openrouter.ai/)) to generate a reflective developer journal entry — written in the voice of an experienced software engineer summarizing the day's work. Pick any model OpenRouter supports (Claude, GPT-4o, Gemini, Llama, etc.) and swap it any time via env var.

## Features

- **Daily GitHub activity scraping** — pulls commits, pushes, and pull request activity across repos (including private repos)
- **AI-generated narratives** — configurable model on OpenRouter transforms raw commits into thoughtful journal entries
- **Model flexibility** — switch between providers by changing a single env var, no code changes
- **No-activity fallback** — on days with zero commits/pushes/PRs, a pre-written entry is used and the AI is not called (saves cost, prevents hallucination)
- **Privacy-first** — private repo names are anonymized, org names stripped, secrets redacted
- **Nightly automation** — GitHub Actions generates entries at midnight UTC and auto-commits
- **CLI tools** — manual entries, specific dates, dry runs, and backfilling
- **Pure markdown output** — logs stored by date in a clean directory structure

## Setup

```bash
git clone <repo-url> && cd captains-log
pip install -r requirements.txt
cp .env.example .env
```

Fill in your `.env`:

| Variable | Description |
|---|---|
| `PERSONAL_GITHUB_TOKEN` | Personal access token (needs `repo` scope) |
| `OPENROUTER_API_KEY` | OpenRouter API key ([get one here](https://openrouter.ai/keys)) |
| `AI_MODEL` | OpenRouter model ID (e.g. `anthropic/claude-sonnet-5`, `openai/gpt-4o`). Defaults to `anthropic/claude-sonnet-5`. |
| `GITHUB_ORGS` | Comma-separated list of GitHub orgs to scrape |
| `GITHUB_USERNAME` | Your GitHub username |

## CLI Usage

```bash
# Generate today's log
python log.py generate

# Generate for a specific date
python log.py generate --date 2026-03-01

# Preview without saving
python log.py generate --dry-run

# Add a manual entry
python log.py add "Discovered an interesting approach to caching"

# Add a manual entry for a specific date
python log.py add "Note text" --date 2026-03-01

# Backfill a range of dates
python log.py backfill --since 2026-01-01 --until 2026-03-01
```

## GitHub Actions

The nightly workflow runs at midnight UTC, generates the previous day's entry, and auto-commits it to the repo.

Add these in repo **Settings → Secrets and variables → Actions**:

- `PERSONAL_GITHUB_TOKEN` (secret)
- `OPENROUTER_API_KEY` (secret)
- `AI_MODEL` (variable — model names aren't sensitive, e.g. `anthropic/claude-sonnet-5`)

## Log Format

Entries are stored as markdown files organized by date:

```
logs/
└── 2026/
    └── 03/
        └── 2026-03-01.md
```

Each file contains the AI-generated journal entry for that day.

---
