import re
from copy import deepcopy

from src.config import get_config

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),
    re.compile(r"gho_[A-Za-z0-9]{36,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"token=[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"https?://[^@\s]+:[^@\s]+@[^\s]+"),
]


def _scrub_secrets(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _strip_org_names(text: str, orgs: list[str]) -> str:
    for org in orgs:
        text = re.sub(re.escape(org), "the team", text, flags=re.IGNORECASE)
    return text


def _sanitize_repo(repo: str, is_private: bool, private_map: dict[str, str]) -> str:
    if not is_private:
        return repo.split("/", 1)[-1]

    if repo not in private_map:
        private_map[repo] = f"private-project-{len(private_map) + 1}"
    return private_map[repo]


def sanitize_commits(commits: list[dict]) -> list[dict]:
    config = get_config()
    orgs = config.github_orgs
    private_map: dict[str, str] = {}
    result = []

    for commit in commits:
        sanitized = deepcopy(commit)
        sanitized["repo"] = _sanitize_repo(
            commit["repo"], commit["is_private"], private_map
        )
        message = commit["message"]
        message = _strip_org_names(message, orgs)
        message = _scrub_secrets(message)
        sanitized["message"] = message
        result.append(sanitized)

    return result
