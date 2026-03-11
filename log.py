import datetime

import click

from src.scraper import scrape_daily_activity
from src.sanitizer import sanitize_activity
from src.generator import generate_log_entry
from src.writer import write_log_entry, add_manual_entry


DATE_TYPE = click.DateTime(formats=["%Y-%m-%d"])


@click.group()
def cli():
    pass


@cli.command()
@click.option("--date", type=DATE_TYPE, default=None)
@click.option("--dry-run", is_flag=True, default=False)
def generate(date, dry_run):
    target = date.date() if date else datetime.date.today()

    click.echo(f"Scraping activity for {target}...")
    activity = scrape_daily_activity(since=target)
    sanitized = sanitize_activity(activity)

    click.echo("Generating log entry...")
    narrative = generate_log_entry(
        date=target,
        commits=sanitized["commits"],
        pushes=sanitized["pushes"],
        pull_requests=sanitized["pull_requests"],
    )

    if dry_run:
        click.echo(narrative)
    else:
        path = write_log_entry(
            date=target,
            narrative=narrative,
            commits=sanitized["commits"],
            manual_entries=[],
        )
        click.echo(f"Written to {path}")


@cli.command()
@click.argument("text")
@click.option("--date", type=DATE_TYPE, default=None)
def add(text, date):
    target = date.date() if date else datetime.date.today()
    path = add_manual_entry(date=target, entry_text=text)
    click.echo(f"Added manual entry to {path}")


@cli.command()
@click.option("--since", type=DATE_TYPE, required=True)
@click.option("--until", type=DATE_TYPE, required=True)
def backfill(since, until):
    start = since.date()
    end = until.date()
    current = start

    while current <= end:
        click.echo(f"Scraping activity for {current}...")
        activity = scrape_daily_activity(since=current)
        sanitized = sanitize_activity(activity)

        click.echo(f"Generating log entry for {current}...")
        narrative = generate_log_entry(
            date=current,
            commits=sanitized["commits"],
            pushes=sanitized["pushes"],
            pull_requests=sanitized["pull_requests"],
        )

        path = write_log_entry(
            date=current,
            narrative=narrative,
            commits=sanitized["commits"],
            manual_entries=[],
            overwrite=True,
        )
        click.echo(f"Written to {path}")

        current += datetime.timedelta(days=1)


if __name__ == "__main__":
    cli()
