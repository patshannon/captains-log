# 📓 Captain's Log

**Your daily engineering journal, automated.**

Captain's Log scrapes your GitHub commits and uses AI (Claude Sonnet 4.6) to generate a reflective developer journal entry — written in the voice of an experienced software engineer summarizing the day's work.

## Features

- **Multi-org commit scraping** — pulls commits from multiple GitHub orgs, including private repos
- **AI-generated narratives** — Claude Sonnet 4.6 transforms raw commits into thoughtful journal entries
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
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
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

Add these as **repository secrets**:

- `PERSONAL_GITHUB_TOKEN`
- `ANTHROPIC_API_KEY`

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
