from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


_NOTES_EXPORT_JXA = r"""
const Notes = Application("Notes");
const exported = [];
let skipped = 0;

for (const note of Notes.notes()) {
    try {
        if (note.passwordProtected()) {
            skipped += 1;
            continue;
        }
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
            ["osascript", "-l", "JavaScript", _NOTES_EXPORT_JXA],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise NotesExportError(
            "Apple Notes sync failed because osascript is unavailable."
        ) from error
    except subprocess.CalledProcessError as error:
        raise NotesExportError(
            "Apple Notes sync needs macOS Automation permission. Allow access "
            "under System Settings > Privacy & Security > Automation."
        ) from error

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
