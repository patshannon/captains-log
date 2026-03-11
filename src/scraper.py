import datetime

from github import Auth, Github, GithubException, RateLimitExceededException

from src.config import get_config


def _commit_to_dict(
    commit,
    fallback_repo_name: str | None = None,
    fallback_private: bool = False,
) -> dict:
    repo = commit.repository
    repo_name = repo.full_name if repo else fallback_repo_name
    is_private = repo.private if repo else fallback_private

    if not repo_name:
        raise ValueError("Commit repository name is unavailable")

    try:
        files_changed = sum(1 for _ in commit.files)
    except GithubException:
        files_changed = 0

    return {
        "repo": repo_name,
        "message": commit.commit.message.split("\n", 1)[0],
        "sha": commit.sha[:7],
        "timestamp": commit.commit.author.date.isoformat(),
        "files_changed": files_changed,
        "is_private": is_private,
    }


def _is_user_commit(commit, username: str) -> bool:
    author_login = commit.author.login if commit.author else None
    committer_login = commit.committer.login if commit.committer else None
    return author_login == username or committer_login == username


def _is_in_date_range(
    commit, since: datetime.date, until: datetime.date
) -> bool:
    authored_on = commit.commit.author.date.date()
    committed_on = commit.commit.committer.date.date()
    return (
        since <= authored_on <= until
        or since <= committed_on <= until
    )


def _iter_user_events_for_range(
    g: Github, username: str, since: datetime.date, until: datetime.date
):
    for event in g.get_user(username).get_events():
        event_date = event.created_at.date()
        if event_date < since:
            break
        if event_date > until:
            continue
        yield event


def _scrape_commits_from_user_activity(
    g: Github, username: str, since: datetime.date, until: datetime.date
) -> list[dict]:
    refs: set[tuple[str, str]] = set()

    for event in _iter_user_events_for_range(g, username, since, until):
        if event.type == "PushEvent":
            for commit in event.payload.get("commits", []):
                sha = commit.get("sha")
                if sha and event.repo:
                    refs.add((event.repo.name, sha))
            head_sha = event.payload.get("head")
            if head_sha and event.repo:
                refs.add((event.repo.name, head_sha))
            continue

        if event.type == "PullRequestEvent":
            pull_request = event.payload.get("pull_request", {})
            head = pull_request.get("head", {})
            sha = head.get("sha")
            repo_name = head.get("repo", {}).get("full_name")
            if not repo_name and event.repo:
                repo_name = event.repo.name
            if sha and repo_name:
                refs.add((repo_name, sha))

    commits = []
    for repo_name, sha in refs:
        try:
            repo = g.get_repo(repo_name)
            commit = repo.get_commit(sha)
        except GithubException:
            continue

        if not _is_user_commit(commit, username):
            continue
        if not _is_in_date_range(commit, since, until):
            continue

        commits.append(
            _commit_to_dict(
                commit,
                fallback_repo_name=repo.full_name,
                fallback_private=repo.private,
            )
        )

    return commits


def _search_commits(
    g: Github, username: str, since: datetime.date, until: datetime.date
) -> list[dict]:
    if since == until:
        date_filter = f"committer-date:{since.isoformat()}"
    else:
        date_filter = f"committer-date:{since.isoformat()}..{until.isoformat()}"

    query = f"author:{username} {date_filter}"

    commits = []
    for commit in g.search_commits(query):
        commits.append(_commit_to_dict(commit))
    return commits


def _merge_commits(primary: list[dict], secondary: list[dict]) -> list[dict]:
    merged: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for commit in primary + secondary:
        key = (commit["repo"], commit["sha"])
        if key in seen:
            continue
        seen.add(key)
        merged.append(commit)

    return merged


def _scrape_non_commit_activity_from_user_events(
    g: Github, username: str, since: datetime.date, until: datetime.date
) -> tuple[list[dict], list[dict]]:
    repo_cache: dict[str, object | None] = {}
    pushes: list[dict] = []
    pull_requests: list[dict] = []

    def _get_repo(repo_name: str):
        if repo_name in repo_cache:
            return repo_cache[repo_name]
        try:
            repo = g.get_repo(repo_name)
        except GithubException:
            repo = None
        repo_cache[repo_name] = repo
        return repo

    for event in _iter_user_events_for_range(g, username, since, until):
        if event.type == "PushEvent" and event.repo:
            ref = event.payload.get("ref", "")
            branch = ref.replace("refs/heads/", "") if ref else "unknown"
            commits_pushed = event.payload.get("distinct_size")
            if commits_pushed is None:
                commits_pushed = event.payload.get("size", 0)
            if not commits_pushed:
                commits_pushed = len(event.payload.get("commits", []))
            repo_name = event.repo.name
            repo = _get_repo(repo_name)
            pushes.append({
                "repo": repo_name,
                "branch": branch,
                "commits_pushed": int(commits_pushed),
                "timestamp": event.created_at.isoformat(),
                "is_private": bool(repo.private) if repo else False,
            })
            continue

        if event.type == "PullRequestEvent":
            pull_request = event.payload.get("pull_request", {})
            head = pull_request.get("head", {})
            repo_name = head.get("repo", {}).get("full_name")
            if not repo_name and event.repo:
                repo_name = event.repo.name
            if not repo_name:
                continue

            repo = _get_repo(repo_name)
            number = pull_request.get("number")
            title = pull_request.get("title", "").strip()
            if not title and number is not None and repo:
                try:
                    title = repo.get_pull(number).title
                except GithubException:
                    title = ""

            pull_requests.append({
                "repo": repo_name,
                "number": number,
                "title": title,
                "action": event.payload.get("action", "updated"),
                "state": pull_request.get("state", "open"),
                "merged": bool(pull_request.get("merged", False)),
                "timestamp": event.created_at.isoformat(),
                "is_private": bool(repo.private) if repo else False,
            })

    pushes.sort(key=lambda p: p["timestamp"], reverse=True)
    pull_requests.sort(key=lambda pr: pr["timestamp"], reverse=True)
    return pushes, pull_requests


def _scrape_commits_with_client(
    g: Github, username: str, since: datetime.date, until: datetime.date
) -> list[dict]:
    search_commits: list[dict] = []
    activity_commits: list[dict] = []

    try:
        search_commits = _search_commits(g, username, since, until)
    except RateLimitExceededException:
        print("Warning: GitHub rate limit hit during commit search")
    except GithubException as e:
        print(f"Warning: commit search failed: {e}")

    try:
        activity_commits = _scrape_commits_from_user_activity(
            g=g,
            username=username,
            since=since,
            until=until,
        )
    except RateLimitExceededException:
        print("Warning: GitHub rate limit hit during activity fallback")
    except GithubException as e:
        print(f"Warning: activity fallback failed: {e}")

    commits = _merge_commits(search_commits, activity_commits)
    commits.sort(key=lambda c: c["timestamp"], reverse=True)
    return commits


def scrape_commits(
    since: datetime.date, until: datetime.date | None = None
) -> list[dict]:
    if until is None:
        until = since

    config = get_config()
    g = Github(auth=Auth.Token(config.personal_github_token))
    return _scrape_commits_with_client(g, config.github_username, since, until)


def scrape_daily_activity(
    since: datetime.date, until: datetime.date | None = None
) -> dict:
    if until is None:
        until = since

    config = get_config()
    g = Github(auth=Auth.Token(config.personal_github_token))

    commits = _scrape_commits_with_client(g, config.github_username, since, until)
    pushes, pull_requests = _scrape_non_commit_activity_from_user_events(
        g, config.github_username, since, until
    )

    return {
        "commits": commits,
        "pushes": pushes,
        "pull_requests": pull_requests,
    }
