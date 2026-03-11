import datetime
from pathlib import Path

import anthropic

from src.config import get_config

SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"


def _load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def _build_user_message(
    date: datetime.date,
    commits: list[dict],
    pushes: list[dict] | None = None,
    pull_requests: list[dict] | None = None,
    manual_entries: list[str] | None = None,
) -> str:
    pushes = pushes or []
    pull_requests = pull_requests or []

    day_of_year = date.timetuple().tm_yday
    lines = [
        f"Date: {date.isoformat()} (Day {day_of_year} of {date.year})",
        "",
    ]

    if commits:
        lines.append(f"Commits ({len(commits)}):")
        for c in commits:
            lines.append(
                f"- [{c['repo']}] {c['message']} "
                f"(sha: {c['sha'][:7]}, files changed: {c['files_changed']})"
            )
    else:
        lines.append("No commits today.")

    lines.append("")
    if pushes:
        lines.append(f"Pushes ({len(pushes)}):")
        for push in pushes:
            lines.append(
                f"- [{push['repo']}] pushed to {push['branch']} "
                f"(commits: {push['commits_pushed']})"
            )
    else:
        lines.append("No pushes today.")

    lines.append("")
    if pull_requests:
        lines.append(f"Pull requests ({len(pull_requests)}):")
        for pull_request in pull_requests:
            number = pull_request.get("number")
            number_text = f"#{number}" if number is not None else "#?"
            lines.append(
                f"- [{pull_request['repo']}] {pull_request['action']} "
                f"{number_text}: {pull_request['title']}"
            )
    else:
        lines.append("No pull requests today.")

    if manual_entries:
        lines.append("")
        lines.append("Manual notes:")
        for entry in manual_entries:
            lines.append(f"- {entry}")

    return "\n".join(lines)


def generate_log_entry(
    date: datetime.date,
    commits: list[dict],
    pushes: list[dict] | None = None,
    pull_requests: list[dict] | None = None,
    manual_entries: list[str] | None = None,
) -> str:
    config = get_config()
    system_prompt = _load_system_prompt()
    user_message = _build_user_message(
        date=date,
        commits=commits,
        pushes=pushes,
        pull_requests=pull_requests,
        manual_entries=manual_entries,
    )

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APIError as e:
        raise RuntimeError(f"Anthropic API call failed: {e}") from e

    return response.content[0].text
