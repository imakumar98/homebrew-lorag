from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_CHAT_MODEL = "llama3.2:3b"
DEFAULT_EMBED_MODEL = "nomic-embed-text"


@dataclass(frozen=True)
class SiftPaths:
    docs_dir: Path
    db_dir: Path
    config_path: Path

    @property
    def notes_dir(self) -> Path:
        return self.docs_dir / "apple-notes"

    @classmethod
    def from_home(cls, home: Path) -> SiftPaths:
        return cls(
            docs_dir=home / "sift" / "docs",
            db_dir=home / ".sift" / "db",
            config_path=home / ".sift" / "config.toml",
        )


@dataclass(frozen=True)
class SiftConfig:
    chat_model: str
    embed_model: str


def ensure_layout(paths: SiftPaths) -> None:
    paths.docs_dir.mkdir(parents=True, exist_ok=True)
    paths.config_path.parent.mkdir(parents=True, exist_ok=True)


def load_config(paths: SiftPaths) -> SiftConfig:
    if not paths.config_path.exists():
        return SiftConfig(DEFAULT_CHAT_MODEL, DEFAULT_EMBED_MODEL)

    import tomllib

    data = tomllib.loads(paths.config_path.read_text(encoding="utf-8"))
    return SiftConfig(
        chat_model=str(data.get("chat_model", DEFAULT_CHAT_MODEL)),
        embed_model=str(data.get("embed_model", DEFAULT_EMBED_MODEL)),
    )


def write_default_config(paths: SiftPaths) -> None:
    if paths.config_path.exists():
        return
    ensure_layout(paths)
    paths.config_path.write_text(
        (
            f'chat_model = "{DEFAULT_CHAT_MODEL}"\n'
            f'embed_model = "{DEFAULT_EMBED_MODEL}"\n'
        ),
        encoding="utf-8",
    )


def set_chat_model(paths: SiftPaths, chat_model: str) -> None:
    config = load_config(paths)
    ensure_layout(paths)
    paths.config_path.write_text(
        (
            f'chat_model = "{chat_model}"\n'
            f'embed_model = "{config.embed_model}"\n'
        ),
        encoding="utf-8",
    )
