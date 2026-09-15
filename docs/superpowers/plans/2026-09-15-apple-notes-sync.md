# Apple Notes Sync CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `python notes_cli.py sync` to export accessible Apple Notes as local text documents and automatically rebuild the RAG index.

**Architecture:** A single CLI module calls Notes through JXA via `osascript`, validates its JSON response, stages UTF-8 exports, and replaces only the managed `docs/apple-notes/` directory. Sync orchestration deletes and rebuilds `db/` only after export succeeds; tests replace automation and indexing dependencies so real Notes are never accessed.

**Tech Stack:** Python 3.14 standard library, JavaScript for Automation (JXA), macOS `osascript`, existing Chroma/LangChain indexer, `unittest`.

---

## File Structure

- Create `notes_cli.py`: Notes automation, export staging, index rebuild, and CLI parsing.
- Create `tests/test_notes_cli.py`: isolated unit and orchestration tests.
- Create `.gitignore`: prevents generated note text and vector data from being committed.

### Task 1: Parse and stage note exports

**Files:**
- Create: `tests/test_notes_cli.py`
- Create: `notes_cli.py`

- [ ] **Step 1: Write failing tests for payload validation, stable filenames, and export replacement**

```python
import json
import tempfile
import unittest
from pathlib import Path

import notes_cli


class NoteExportTests(unittest.TestCase):
    def test_parse_export_payload_returns_notes_and_skipped_count(self):
        payload = json.dumps({
            "notes": [{"id": "note/1", "title": "Ideas", "body": "Build it"}],
            "skipped": 2,
        })

        notes, skipped = notes_cli.parse_export_payload(payload)

        self.assertEqual(notes, [notes_cli.AppleNote("note/1", "Ideas", "Build it")])
        self.assertEqual(skipped, 2)

    def test_parse_export_payload_rejects_invalid_output(self):
        with self.assertRaises(notes_cli.NotesExportError):
            notes_cli.parse_export_payload('{"notes": "invalid", "skipped": 0}')

    def test_note_filename_is_stable_and_hides_note_id(self):
        filename = notes_cli.note_filename("x-coredata://private-id")

        self.assertEqual(filename, notes_cli.note_filename("x-coredata://private-id"))
        self.assertTrue(filename.endswith(".txt"))
        self.assertNotIn("private-id", filename)

    def test_write_export_replaces_only_managed_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            export_dir.mkdir(parents=True)
            (export_dir / "stale.txt").write_text("stale", encoding="utf-8")
            other_doc = root / "docs" / "keep.txt"
            other_doc.write_text("keep", encoding="utf-8")

            notes_cli.write_export(
                [notes_cli.AppleNote("1", "Ideas", "Build it")],
                export_dir,
            )

            files = list(export_dir.glob("*.txt"))
            self.assertEqual(len(files), 1)
            self.assertFalse((export_dir / "stale.txt").exists())
            self.assertEqual(other_doc.read_text(encoding="utf-8"), "keep")
            self.assertEqual(
                files[0].read_text(encoding="utf-8"),
                "Title: Ideas\n\nBuild it\n",
            )
```

- [ ] **Step 2: Run tests and verify the feature is absent**

Run: `python -m unittest tests.test_notes_cli.NoteExportTests -v`

Expected: FAIL because `notes_cli` does not exist.

- [ ] **Step 3: Implement the export model and helpers**

```python
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
        raw_notes = data["notes"]
        skipped = data["skipped"]
        if not isinstance(raw_notes, list) or not isinstance(skipped, int):
            raise TypeError
        notes = [
            AppleNote(item["id"], item["title"], item["body"])
            for item in raw_notes
            if all(isinstance(item.get(key), str) for key in ("id", "title", "body"))
        ]
        if len(notes) != len(raw_notes):
            raise TypeError
        return notes, skipped
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise NotesExportError("Notes returned invalid export data.") from error


def note_filename(note_id: str) -> str:
    digest = hashlib.sha256(note_id.encode("utf-8")).hexdigest()[:20]
    return f"{digest}.txt"


def write_export(notes: list[AppleNote], export_dir: Path) -> None:
    export_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".apple-notes-", dir=export_dir.parent))
    try:
        for note in notes:
            text = f"Title: {note.title.strip()}\n\n{note.body.strip()}\n"
            (staging / note_filename(note.note_id)).write_text(text, encoding="utf-8")
        if export_dir.exists():
            shutil.rmtree(export_dir)
        staging.replace(export_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
```

- [ ] **Step 4: Run the focused tests**

Run: `python -m unittest tests.test_notes_cli.NoteExportTests -v`

Expected: all four tests PASS.

- [ ] **Step 5: Commit the export core**

```bash
git add notes_cli.py tests/test_notes_cli.py
git commit -m "feat: add staged Apple Notes text export"
```

### Task 2: Retrieve accessible notes through macOS automation

**Files:**
- Modify: `notes_cli.py`
- Modify: `tests/test_notes_cli.py`

- [ ] **Step 1: Add failing automation tests**

```python
import subprocess
from unittest.mock import Mock, patch


class NotesAutomationTests(unittest.TestCase):
    @patch("notes_cli.sys.platform", "darwin")
    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_uses_jxa_without_printing_content(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout='{"notes":[{"id":"1","title":"Private","body":"secret"}],"skipped":1}',
            stderr="",
        )

        notes, skipped = notes_cli.fetch_notes()

        self.assertEqual(notes, [notes_cli.AppleNote("1", "Private", "secret")])
        self.assertEqual(skipped, 1)
        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["osascript", "-l", "JavaScript"])

    @patch("notes_cli.sys.platform", "linux")
    def test_fetch_notes_rejects_non_macos(self):
        with self.assertRaisesRegex(notes_cli.NotesExportError, "macOS"):
            notes_cli.fetch_notes()

    @patch("notes_cli.sys.platform", "darwin")
    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_explains_automation_failure(self, run):
        run.side_effect = subprocess.CalledProcessError(
            1, ["osascript"], stderr="Not authorized to send Apple events"
        )

        with self.assertRaisesRegex(notes_cli.NotesExportError, "permission"):
            notes_cli.fetch_notes()
```

- [ ] **Step 2: Run tests and verify missing automation behavior**

Run: `python -m unittest tests.test_notes_cli.NotesAutomationTests -v`

Expected: FAIL because `fetch_notes` is not defined.

- [ ] **Step 3: Add the JXA script and subprocess adapter**

```python
import subprocess
import sys


JXA_EXPORT_SCRIPT = r"""
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

JSON.stringify({notes: exported, skipped: skipped});
"""


def fetch_notes() -> tuple[list[AppleNote], int]:
    if sys.platform != "darwin":
        raise NotesExportError("Apple Notes sync is available only on macOS.")
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", JXA_EXPORT_SCRIPT],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise NotesExportError("osascript is unavailable on this Mac.") from error
    except subprocess.CalledProcessError as error:
        raise NotesExportError(
            "Could not access Apple Notes. Grant automation permission to your terminal "
            "or Cursor in System Settings > Privacy & Security > Automation."
        ) from error
    return parse_export_payload(result.stdout)
```

- [ ] **Step 4: Run automation and export tests**

Run: `python -m unittest tests.test_notes_cli -v`

Expected: all seven tests PASS without opening Notes or requesting permission.

- [ ] **Step 5: Commit the automation adapter**

```bash
git add notes_cli.py tests/test_notes_cli.py
git commit -m "feat: read unlocked notes through macOS automation"
```

### Task 3: Add sync orchestration, CLI, and privacy exclusions

**Files:**
- Modify: `notes_cli.py`
- Modify: `tests/test_notes_cli.py`
- Create: `.gitignore`

- [ ] **Step 1: Add failing orchestration and command tests**

```python
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO


class NotesSyncTests(unittest.TestCase):
    def test_sync_exports_before_removing_and_rebuilding_db(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            db_dir = root / "db"
            db_dir.mkdir()
            (db_dir / "old").write_text("old", encoding="utf-8")
            rebuilt = []

            count, skipped = notes_cli.sync_notes(
                export_dir,
                db_dir,
                fetch=lambda: ([notes_cli.AppleNote("1", "One", "Body")], 2),
                rebuild=lambda docs, db: rebuilt.append((docs, db)),
            )

            self.assertEqual((count, skipped), (1, 2))
            self.assertFalse((db_dir / "old").exists())
            self.assertEqual(rebuilt, [(export_dir.parent, db_dir)])

    def test_sync_preserves_db_when_fetch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_dir = root / "db"
            db_dir.mkdir()
            marker = db_dir / "old"
            marker.write_text("old", encoding="utf-8")

            with self.assertRaises(notes_cli.NotesExportError):
                notes_cli.sync_notes(
                    root / "docs" / "apple-notes",
                    db_dir,
                    fetch=lambda: (_ for _ in ()).throw(
                        notes_cli.NotesExportError("denied")
                    ),
                    rebuild=lambda docs, db: None,
                )

            self.assertTrue(marker.exists())

    @patch("notes_cli.sync_notes", return_value=(3, 1))
    def test_main_reports_counts_without_note_content(self, sync):
        output = StringIO()

        with redirect_stdout(output):
            exit_code = notes_cli.main(["sync"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Exported 3 notes", output.getvalue())
        self.assertIn("Skipped 1", output.getvalue())

    @patch("notes_cli.sync_notes", side_effect=notes_cli.NotesExportError("denied"))
    def test_main_returns_error_status(self, sync):
        errors = StringIO()

        with redirect_stderr(errors):
            exit_code = notes_cli.main(["sync"])

        self.assertEqual(exit_code, 1)
        self.assertIn("denied", errors.getvalue())
```

- [ ] **Step 2: Run tests and verify orchestration is absent**

Run: `python -m unittest tests.test_notes_cli.NotesSyncTests -v`

Expected: FAIL because `sync_notes` and `main` are not defined.

- [ ] **Step 3: Implement rebuild, orchestration, and CLI parsing**

```python
import argparse
from collections.abc import Callable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_EXPORT_DIR = PROJECT_ROOT / "docs" / "apple-notes"
DEFAULT_DB_DIR = PROJECT_ROOT / "db"


def rebuild_index(docs_dir: Path, db_dir: Path) -> None:
    import main as rag

    rag.DOCS_DIR = str(docs_dir)
    rag.DB_DIR = str(db_dir)
    rag.get_vectorstore()


def sync_notes(
    export_dir: Path = DEFAULT_EXPORT_DIR,
    db_dir: Path = DEFAULT_DB_DIR,
    *,
    fetch: Callable[[], tuple[list[AppleNote], int]] = fetch_notes,
    rebuild: Callable[[Path, Path], None] = rebuild_index,
) -> tuple[int, int]:
    notes, skipped = fetch()
    write_export(notes, export_dir)
    if db_dir.exists():
        shutil.rmtree(db_dir)
    rebuild(export_dir.parent, db_dir)
    return len(notes), skipped


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync Apple Notes into local RAG.")
    parser.add_subparsers(dest="command", required=True).add_parser(
        "sync", help="Export accessible notes and rebuild the vector index."
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "sync":
            count, skipped = sync_notes()
            print(f"Exported {count} notes. Skipped {skipped}. Index rebuilt.")
            return 0
    except NotesExportError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Exclude private generated data from Git**

Create `.gitignore`:

```gitignore
db/
docs/apple-notes/
__pycache__/
```

- [ ] **Step 5: Run the complete test suite**

Run: `python -m unittest discover -s tests -v`

Expected: all eleven tests PASS and no Notes permission dialog appears.

- [ ] **Step 6: Verify CLI help and syntax without accessing Notes**

Run: `python notes_cli.py --help && python -m py_compile notes_cli.py main.py`

Expected: help lists the `sync` command and compilation exits successfully.

- [ ] **Step 7: Commit the completed CLI**

```bash
git add notes_cli.py tests/test_notes_cli.py .gitignore
git commit -m "feat: add Apple Notes sync command"
```

## Manual Run

The user runs this command because it accesses personal Notes and may trigger a macOS permission prompt:

```bash
python notes_cli.py sync
```

Expected: macOS requests Notes automation access on first use; after approval, the command reports exported/skipped counts and rebuilds the index without printing note content.
