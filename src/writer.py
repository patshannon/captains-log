"""Markdown writer module — assembles Captain's Log entries into markdown files."""

import datetime
from pathlib import Path


def date_to_stardate(date: datetime.date) -> str:
    """Convert a date to stardate format YYYY.DDD (day of year, zero-padded)."""
    day_of_year = date.timetuple().tm_yday
    return f"{date.year}.{day_of_year:03d}"


def _log_path(date: datetime.date, log_dir: str = "logs") -> Path:
    return Path(log_dir) / f"{date.year:04d}" / f"{date.month:02d}" / f"{date.strftime('%Y-%m-%d')}.md"


def _format_manual_entries(manual_entries: list[str]) -> str | None:
    if not manual_entries:
        return None

    lines = ["## Manual Entries", ""]
    for entry in manual_entries:
        lines.append(f"- {entry}")
    return "\n".join(lines)


def _build_entry(date: datetime.date, narrative: str, commits: list[dict],
                 manual_entries: list[str]) -> str:
    stardate = date_to_stardate(date)

    sections = [
        f"# Captain's Log — {date.strftime('%Y-%m-%d')}",
        narrative,
    ]

    manual_section = _format_manual_entries(manual_entries)
    if manual_section:
        sections.append("")
        sections.append("---")
        sections.append("")
        sections.append(manual_section)

    sections.append("")
    return "\n".join(sections)


def write_log_entry(date: datetime.date, narrative: str, commits: list[dict],
                    manual_entries: list[str], log_dir: str = "logs") -> Path:
    """Write (or append to) a daily markdown log file.

    Returns the path to the written file.
    """
    path = _log_path(date, log_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = _build_entry(date, narrative, commits, manual_entries)

    if path.exists():
        existing = path.read_text()
        path.write_text(existing.rstrip("\n") + "\n\n---\n\n" + entry)
    else:
        path.write_text(entry)

    return path


def add_manual_entry(date: datetime.date, entry_text: str, log_dir: str = "logs") -> Path:
    """Add a manual entry to an existing log file, or create a minimal one.

    Returns the path to the written file.
    """
    path = _log_path(date, log_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        # Create a minimal log with just the manual entry
        content = _build_entry(date, "*No narrative recorded.*", [], [entry_text])
        path.write_text(content)
        return path

    existing = path.read_text()

    if "## Manual Entries" in existing:
        # Append to existing Manual Entries section
        existing = existing.rstrip("\n")
        existing += f"\n- {entry_text}\n"
        path.write_text(existing)
    else:
        # Append a new Manual Entries section
        existing = existing.rstrip("\n")
        existing += "\n\n---\n\n## Manual Entries\n\n"
        existing += f"- {entry_text}\n"
        path.write_text(existing)

    return path
