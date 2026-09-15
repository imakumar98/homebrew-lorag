from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


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
        ):
            raise TypeError

        notes = []
        for item in raw_notes:
            if not isinstance(item, dict):
                raise TypeError
            note_id = item["id"]
            title = item["title"]
            body = item["body"]
            if not all(isinstance(value, str) for value in (note_id, title, body)):
                raise TypeError
            notes.append(AppleNote(note_id, title, body))
        return notes, skipped
    except (KeyError, TypeError, ValueError) as error:
        raise NotesExportError("Notes returned invalid export data.") from error


def note_filename(note_id: str) -> str:
    digest = hashlib.sha256(note_id.encode("utf-8")).hexdigest()[:20]
    return f"{digest}.txt"


def write_export(notes: list[AppleNote], export_dir: Path) -> None:
    export_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".apple-notes-", dir=export_dir.parent))
    try:
        for note in notes:
            content = f"Title: {note.title.strip()}\n\n{note.body.strip()}\n"
            (staging / note_filename(note.note_id)).write_text(
                content,
                encoding="utf-8",
            )
        if export_dir.exists():
            shutil.rmtree(export_dir)
        staging.replace(export_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
