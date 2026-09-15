from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_EXPORT_DIR = PROJECT_ROOT / "docs" / "apple-notes"
DEFAULT_DB_DIR = PROJECT_ROOT / "db"


_NOTES_EXPORT_JXA = r"""
const Notes = Application("Notes");
const exported = [];
let skipped = 0;

for (const note of Notes.notes()) {
    try {
        exported.push({
            id: String(note.id()),
            title: String(note.name() || ""),
            body: String(note.plaintext() || "")
        });
    } catch (error) {
        skipped += 1;
    }
}

JSON.stringify({notes: exported, skipped});
""".strip()


class NotesExportError(RuntimeError):
    pass


@dataclass(frozen=True)
class AppleNote:
    note_id: str
    title: str
    body: str


FetchNotes = Callable[[], tuple[list[AppleNote], int]]
RebuildIndex = Callable[[Path, Path], None]


def parse_export_payload(payload: str) -> tuple[list[AppleNote], int]:
    try:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise TypeError

        raw_notes = data["notes"]
        skipped = data["skipped"]
        if (
            not isinstance(raw_notes, list)
            or not isinstance(skipped, int)
            or isinstance(skipped, bool)
            or skipped < 0
        ):
            raise TypeError

        notes = []
        note_ids = set()
        for item in raw_notes:
            if not isinstance(item, dict) or set(item) != {"id", "title", "body"}:
                raise TypeError
            note_id = item["id"]
            title = item["title"]
            body = item["body"]
            if not all(isinstance(value, str) for value in (note_id, title, body)):
                raise TypeError
            if not note_id or note_id in note_ids:
                raise TypeError
            note_ids.add(note_id)
            notes.append(AppleNote(note_id, title, body))
        return notes, skipped
    except (KeyError, TypeError, ValueError) as error:
        raise NotesExportError("Notes returned invalid export data.") from error


def fetch_notes() -> tuple[list[AppleNote], int]:
    if sys.platform != "darwin":
        raise NotesExportError("Apple Notes sync is macOS-only.")

    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", _NOTES_EXPORT_JXA],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise NotesExportError(
            "Apple Notes sync failed because osascript is unavailable."
        ) from error
    except subprocess.CalledProcessError as error:
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        authorization_signals = ("-1743", "not authorized", "not permitted")
        if any(signal in stderr.lower() for signal in authorization_signals):
            raise NotesExportError(
                "Apple Notes sync needs macOS Automation permission. Allow "
                "access under System Settings > Privacy & Security > "
                "Automation."
            ) from error
        raise NotesExportError("Apple Notes automation failed.") from error

    return parse_export_payload(result.stdout)


def note_filename(note_id: str) -> str:
    digest = hashlib.sha256(note_id.encode("utf-8")).hexdigest()[:20]
    return f"{digest}.txt"


def write_export(notes: list[AppleNote], export_dir: Path) -> None:
    export_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".apple-notes-", dir=export_dir.parent))
    backup = None
    try:
        for note in notes:
            content = f"Title: {note.title.strip()}\n\n{note.body.strip()}\n"
            (staging / note_filename(note.note_id)).write_text(
                content,
                encoding="utf-8",
            )
        if export_dir.exists():
            backup = Path(
                tempfile.mkdtemp(
                    prefix=".apple-notes-backup-",
                    dir=export_dir.parent,
                )
            )
            backup.rmdir()
            export_dir.replace(backup)
        try:
            staging.replace(export_dir)
        except Exception:
            if backup is not None:
                backup.replace(export_dir)
            raise
        if backup is not None:
            shutil.rmtree(backup)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def rebuild_index(
    docs_dir: Path,
    db_dir: Path,
    embed_model: str = "nomic-embed-text",
) -> None:
    import main as rag

    rag.get_vectorstore(docs_dir, db_dir, embed_model)


def _unused_hidden_path(parent: Path, prefix: str) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
    path.rmdir()
    return path


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists() or path.is_symlink():
        try:
            path.unlink()
        except OSError:
            pass


def _refresh_index(
    docs_dir: Path,
    db_dir: Path,
    rebuild: RebuildIndex,
) -> None:
    staging = _unused_hidden_path(
        db_dir.parent,
        f".{db_dir.name}-staging-",
    )
    backup: Path | None = None

    try:
        rebuild(docs_dir, staging)
        if not staging.exists():
            raise RuntimeError("Index rebuild did not create a database.")

        if db_dir.exists() or db_dir.is_symlink():
            backup = _unused_hidden_path(
                db_dir.parent,
                f".{db_dir.name}-backup-",
            )
            db_dir.replace(backup)

        try:
            staging.replace(db_dir)
        except Exception:
            if backup is not None:
                backup.replace(db_dir)
            raise

        if backup is not None:
            _remove_path(backup)
    except Exception:
        _remove_path(staging)
        if (
            backup is not None
            and (backup.exists() or backup.is_symlink())
            and not (db_dir.exists() or db_dir.is_symlink())
        ):
            backup.replace(db_dir)
        if backup is not None:
            _remove_path(backup)
        raise


def sync_notes(
    export_dir: Path = DEFAULT_EXPORT_DIR,
    db_dir: Path = DEFAULT_DB_DIR,
    *,
    fetch: FetchNotes | None = None,
    rebuild: RebuildIndex | None = None,
) -> tuple[int, int]:
    fetch_fn = fetch_notes if fetch is None else fetch
    rebuild_fn = rebuild_index if rebuild is None else rebuild

    notes, skipped = fetch_fn()
    try:
        write_export(notes, export_dir)
    except NotesExportError:
        raise
    except Exception as error:
        raise NotesExportError("Apple Notes export failed.") from error

    try:
        _refresh_index(export_dir.parent, db_dir, rebuild_fn)
    except Exception as error:
        raise NotesExportError(
            "Notes were exported, but the index rebuild failed."
        ) from error

    return len(notes), skipped


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Sync Apple Notes into local RAG.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("sync", help="Export notes and rebuild the index.")
    args = parser.parse_args(argv)

    if args.command == "sync":
        try:
            exported, skipped = sync_notes()
        except NotesExportError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(
            f"Exported {exported} notes; skipped {skipped}; index rebuilt."
        )
        return 0

    parser.error("a command is required")


if __name__ == "__main__":
    raise SystemExit(main())
