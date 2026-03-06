import datetime

from github import Github, GithubException, RateLimitExceededException

from src.config import get_config


def scrape_commits(
    since: datetime.date, until: datetime.date | None = None
) -> list[dict]:
    if until is None:
        until = since

    config = get_config()
    g = Github(config.github_token)

    # Use the Search API to find commits by author across all accessible repos —
    # far more efficient than iterating every repo in every org.
    if since == until:
        date_filter = f"committer-date:{since.isoformat()}"
    else:
        date_filter = f"committer-date:{since.isoformat()}..{until.isoformat()}"

    query = f"author:{config.github_username} {date_filter}"

    commits = []
    try:
        for commit in g.search_commits(query):
            repo = commit.repository
            try:
                files_changed = sum(1 for _ in commit.files)
            except GithubException:
                files_changed = 0
            commits.append({
                "repo": repo.full_name,
                "message": commit.commit.message.split("\n", 1)[0],
                "sha": commit.sha[:7],
                "timestamp": commit.commit.author.date.isoformat(),
                "files_changed": files_changed,
                "is_private": repo.private,
            })
    except RateLimitExceededException:
        print("Warning: GitHub rate limit hit during commit search")
    except GithubException as e:
        print(f"Warning: commit search failed: {e}")

    commits.sort(key=lambda c: c["timestamp"], reverse=True)
    return commits
