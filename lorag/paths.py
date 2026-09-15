from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_CHAT_MODEL = "llama3.2:3b"
DEFAULT_EMBED_MODEL = "nomic-embed-text"


@dataclass(frozen=True)
class LoragPaths:
    docs_dir: Path
    db_dir: Path
    config_path: Path

    @property
    def notes_dir(self) -> Path:
        return self.docs_dir / "apple-notes"

    @classmethod
    def from_home(cls, home: Path) -> LoragPaths:
        return cls(
            docs_dir=home / "lorag" / "docs",
            db_dir=home / "lorag" / "database",
            config_path=home / ".lorag" / "config.toml",
        )


@dataclass(frozen=True)
class LoragConfig:
    chat_model: str
    embed_model: str


def ensure_layout(paths: LoragPaths) -> None:
    paths.docs_dir.mkdir(parents=True, exist_ok=True)
    paths.config_path.parent.mkdir(parents=True, exist_ok=True)


def load_config(paths: LoragPaths) -> LoragConfig:
    if not paths.config_path.exists():
        return LoragConfig(DEFAULT_CHAT_MODEL, DEFAULT_EMBED_MODEL)

    import tomllib

    data = tomllib.loads(paths.config_path.read_text(encoding="utf-8"))
    return LoragConfig(
        chat_model=str(data.get("chat_model", DEFAULT_CHAT_MODEL)),
        embed_model=str(data.get("embed_model", DEFAULT_EMBED_MODEL)),
    )


def _escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _write_config(paths: LoragPaths, config: LoragConfig) -> None:
    ensure_layout(paths)
    paths.config_path.write_text(
        (
            f'chat_model = "{_escape_toml_string(config.chat_model)}"\n'
            f'embed_model = "{_escape_toml_string(config.embed_model)}"\n'
        ),
        encoding="utf-8",
    )


def write_default_config(paths: LoragPaths) -> None:
    if paths.config_path.exists():
        return
    _write_config(paths, LoragConfig(DEFAULT_CHAT_MODEL, DEFAULT_EMBED_MODEL))


def set_chat_model(paths: LoragPaths, chat_model: str) -> None:
    config = load_config(paths)
    _write_config(paths, LoragConfig(chat_model, config.embed_model))
