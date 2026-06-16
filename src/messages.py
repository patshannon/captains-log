"""Pre-written journal entries used when there is no GitHub activity to summarize.

When a day produces zero commits, zero pushes, and zero pull requests, we skip the
AI call entirely and emit one of these messages at random. This avoids both the
cost of an LLM call and the model's tendency to hallucinate plausible-sounding
context on sparse inputs.
"""

import random


NO_ACTIVITY_MESSAGES: list[str] = [
    "No activity on GitHub today — a quiet day in the log. Sometimes the most "
    "important work happens away from the keyboard: thinking, planning, reading, "
    "or simply resting. The codebase can wait.",

    "Nothing to report. The commit log is empty, no pushes, no pull requests. "
    "A blank day is still a data point — it just means the work didn't happen "
    "in git today.",

    "A silent day in the codebase. No commits, no pushes, no PRs. Could be a "
    "research day, a meeting marathon, or a deliberate step back. Tomorrow's "
    "log will probably look busier.",

    "No activity recorded for today. Rest, research, or the kind of work that "
    "doesn't show up in version control — all valid reasons for a quiet log.",

    "The repositories stayed quiet today. Not every productive day needs a "
    "commit; sometimes the best work is the thinking that happens before any "
    "code gets written.",

    "An empty entry today. The git log has nothing to say, which is fine — not "
    "every day produces artifacts, and not every day should.",

    "Zero commits, zero pushes, zero PRs. A clean slate. The tool is working "
    "correctly; today just didn't generate any activity worth recording.",

    "No signal from GitHub today. Could be a holiday, a sick day, or a "
    "focus-block on something offline. Whatever the reason, the log reflects "
    "it honestly: nothing happened.",

    "A still day in the log. Sometimes the best engineering work is the kind "
    "that takes place in your head — sketching, debating, deciding — long "
    "before anything gets committed.",

    "Quiet log today. No commits, no PRs, no pushes. The codebase rests.",
]


def pick_no_activity_message() -> str:
    """Return a randomly-chosen pre-written entry for a no-activity day."""
    return random.choice(NO_ACTIVITY_MESSAGES)
