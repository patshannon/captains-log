from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
import os


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".env").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


@dataclass
class Config:
    personal_github_token: str
    anthropic_api_key: str
    github_orgs: list[str] = field(default_factory=lambda: ["patshannon"])
    github_username: str = "patshannon"
    log_dir: str = "logs"

    def __init__(self) -> None:
        project_root = _find_project_root()
        load_dotenv(project_root / ".env")

        self.personal_github_token = self._require("PERSONAL_GITHUB_TOKEN")
        self.anthropic_api_key = self._require("ANTHROPIC_API_KEY")
        self.github_orgs = [
            org.strip()
            for org in os.getenv("GITHUB_ORGS", "patshannon").split(",")
            if org.strip()
        ]
        self.github_username = os.getenv("GITHUB_USERNAME", "patshannon")
        self.log_dir = os.getenv("LOG_DIR", "logs")

    @staticmethod
    def _require(var: str) -> str:
        value = os.getenv(var)
        if not value:
            raise EnvironmentError(f"Required environment variable {var} is not set")
        return value


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
