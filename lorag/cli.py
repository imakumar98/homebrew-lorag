from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from lorag import notes as notes_cli
from lorag import rag
from lorag.paths import (
    LoragPaths,
    ensure_layout,
    load_config,
    set_chat_model,
    write_default_config,
)


class ModelPullError(RuntimeError):
    pass


SyncNotes = Callable[..., tuple[int, int]]
PullModel = Callable[[str], None]
Ask = Callable[..., tuple[str, list[str]]]


def paths_for(home: Path) -> LoragPaths:
    return LoragPaths.from_home(home)


def pull_ollama_model(name: str) -> None:
    try:
        subprocess.run(
            ["ollama", "pull", name],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise ModelPullError(
            "Ollama is not installed. Install it with `brew install ollama`."
        ) from error
    except subprocess.CalledProcessError as error:
        raise ModelPullError(
            f"Could not pull model {name}."
        ) from error


def cmd_init(paths: LoragPaths, sync_notes: SyncNotes) -> int:
    ensure_layout(paths)
    write_default_config(paths)
    return cmd_sync(paths, sync_notes)


def cmd_sync(paths: LoragPaths, sync_notes: SyncNotes) -> int:
    try:
        exported, skipped = sync_notes(paths.notes_dir, paths.db_dir)
    except notes_cli.NotesExportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Exported {exported} notes; skipped {skipped}; index rebuilt.")
    return 0


def cmd_question(paths: LoragPaths, query: str, ask: Ask) -> int:
    config = load_config(paths)
    try:
        answer, sources = ask(
            query,
            paths.docs_dir,
            paths.db_dir,
            config.embed_model,
            config.chat_model,
        )
    except rag.QuestionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(answer)
    if sources:
        print()
        print("Sources:")
        for source in sources:
            print(f"- {source}")
    return 0


def cmd_model(paths: LoragPaths) -> int:
    print(load_config(paths).chat_model)
    return 0


def cmd_model_use(paths: LoragPaths, name: str, pull_model: PullModel) -> int:
    try:
        pull_model(name)
    except ModelPullError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    set_chat_model(paths, name)
    print(name)
    return 0


def main(
    argv: list[str] | None = None,
    *,
    home: Path | None = None,
    sync_notes: SyncNotes | None = None,
    pull_model: PullModel | None = None,
    ask: Ask | None = None,
) -> int:
    parser = argparse.ArgumentParser(prog="lorag")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("sync")
    question = sub.add_parser("q")
    question.add_argument("query", nargs="+")
    model = sub.add_parser("model")
    model_sub = model.add_subparsers(dest="model_command")
    use = model_sub.add_parser("use")
    use.add_argument("name")

    args = parser.parse_args(argv)
    paths = paths_for(Path.home() if home is None else home)
    sync_fn = notes_cli.sync_notes if sync_notes is None else sync_notes
    pull_fn = pull_ollama_model if pull_model is None else pull_model
    ask_fn = rag.answer_question if ask is None else ask

    if args.command == "init":
        return cmd_init(paths, sync_fn)
    if args.command == "sync":
        return cmd_sync(paths, sync_fn)
    if args.command == "q":
        return cmd_question(paths, " ".join(args.query), ask_fn)
    if args.command == "model" and args.model_command == "use":
        return cmd_model_use(paths, args.name, pull_fn)
    if args.command == "model":
        return cmd_model(paths)
    parser.error("a command is required")
