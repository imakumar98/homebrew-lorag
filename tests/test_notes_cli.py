import hashlib
import json
import subprocess
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import Mock, patch

import notes_cli


class NoteExportTests(unittest.TestCase):
    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_runs_jxa_and_returns_export(self, run):
        run.return_value = Mock(
            stdout=json.dumps(
                {
                    "notes": [
                        {"id": "note/1", "title": "Ideas", "body": "Build it"}
                    ],
                    "skipped": 3,
                }
            )
        )

        with patch("notes_cli.sys.platform", "darwin"):
            notes, skipped = notes_cli.fetch_notes()

        self.assertEqual(
            notes,
            [notes_cli.AppleNote("note/1", "Ideas", "Build it")],
        )
        self.assertEqual(skipped, 3)
        run.assert_called_once()
        args, kwargs = run.call_args
        self.assertEqual(
            args[0],
            [
                "osascript",
                "-l",
                "JavaScript",
                "-e",
                notes_cli._NOTES_EXPORT_JXA,
            ],
        )
        self.assertIn("Notes.notes()", args[0][4])
        self.assertNotIn("passwordProtected", args[0][4])
        self.assertIn("String(note.id())", args[0][4])
        self.assertIn('String(note.name() || "")', args[0][4])
        self.assertIn('String(note.plaintext() || "")', args[0][4])
        self.assertIn("catch (error)", args[0][4])
        self.assertIn("skipped += 1", args[0][4])
        self.assertIn("JSON.stringify({notes: exported, skipped})", args[0][4])
        self.assertEqual(
            kwargs,
            {"check": True, "capture_output": True, "text": True},
        )

    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_rejects_non_macos_without_subprocess(self, run):
        with patch("notes_cli.sys.platform", "linux"):
            with self.assertRaisesRegex(
                notes_cli.NotesExportError,
                "macOS-only",
            ):
                notes_cli.fetch_notes()

        run.assert_not_called()

    @patch("notes_cli.subprocess.run", side_effect=FileNotFoundError)
    def test_fetch_notes_reports_missing_osascript(self, run):
        with patch("notes_cli.sys.platform", "darwin"):
            with self.assertRaisesRegex(
                notes_cli.NotesExportError,
                "osascript is unavailable",
            ):
                notes_cli.fetch_notes()

    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_reports_automation_permission_failure(self, run):
        authorization_errors = [
            "execution error: Not authorized to send Apple events. (-1743)",
            "Notes is not authorized for automation",
            "Operation not permitted: private note content",
        ]

        for stderr in authorization_errors:
            with self.subTest(stderr=stderr):
                run.side_effect = subprocess.CalledProcessError(
                    1,
                    ["osascript"],
                    stderr=stderr,
                )
                with patch("notes_cli.sys.platform", "darwin"):
                    with self.assertRaises(notes_cli.NotesExportError) as caught:
                        notes_cli.fetch_notes()

                message = str(caught.exception)
                self.assertIn(
                    "System Settings > Privacy & Security > Automation",
                    message,
                )
                self.assertNotIn(stderr, message)

    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_reports_safe_generic_automation_failure(self, run):
        stderr = "Notes failed while reading private note content"
        run.side_effect = subprocess.CalledProcessError(
            1,
            ["osascript"],
            stderr=stderr,
        )

        with patch("notes_cli.sys.platform", "darwin"):
            with self.assertRaises(notes_cli.NotesExportError) as caught:
                notes_cli.fetch_notes()

        message = str(caught.exception)
        self.assertEqual(message, "Apple Notes automation failed.")
        self.assertNotIn(stderr, message)
        self.assertNotIn("System Settings", message)

    @patch("notes_cli.subprocess.run")
    def test_fetch_notes_rejects_invalid_stdout(self, run):
        run.return_value = Mock(stdout="not json")

        with patch("notes_cli.sys.platform", "darwin"):
            with self.assertRaisesRegex(
                notes_cli.NotesExportError,
                "^Notes returned invalid export data\\.$",
            ):
                notes_cli.fetch_notes()

    def test_apple_note_is_frozen(self):
        note = notes_cli.AppleNote("1", "Title", "Body")

        with self.assertRaises(FrozenInstanceError):
            note.title = "Changed"

    def test_parse_export_payload_returns_notes_and_skipped_count(self):
        payload = json.dumps(
            {
                "notes": [
                    {"id": "note/1", "title": "Ideas", "body": "Build it"},
                    {"id": "note/2", "title": "", "body": ""},
                ],
                "skipped": 2,
            }
        )

        notes, skipped = notes_cli.parse_export_payload(payload)

        self.assertEqual(
            notes,
            [
                notes_cli.AppleNote("note/1", "Ideas", "Build it"),
                notes_cli.AppleNote("note/2", "", ""),
            ],
        )
        self.assertEqual(skipped, 2)

    def test_parse_export_payload_rejects_invalid_output(self):
        invalid_payloads = [
            "{not json",
            "[]",
            "{}",
            '{"notes": "invalid", "skipped": 0}',
            '{"notes": [], "skipped": "0"}',
            '{"notes": [], "skipped": true}',
            '{"notes": [{}], "skipped": 0}',
            '{"notes": [{"id": 1, "title": "Title", "body": "Body"}], "skipped": 0}',
            '{"notes": [{"id": "1", "title": null, "body": "Body"}], "skipped": 0}',
            '{"notes": [{"id": "1", "title": "Title", "body": false}], "skipped": 0}',
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    notes_cli.NotesExportError,
                    "^Notes returned invalid export data\\.$",
                ):
                    notes_cli.parse_export_payload(payload)

    def test_parse_export_payload_rejects_extra_note_fields(self):
        payload = json.dumps(
            {
                "notes": [
                    {
                        "id": "1",
                        "title": "Title",
                        "body": "Body",
                        "account": "Private",
                    }
                ],
                "skipped": 0,
            }
        )

        with self.assertRaisesRegex(
            notes_cli.NotesExportError,
            "^Notes returned invalid export data\\.$",
        ):
            notes_cli.parse_export_payload(payload)

    def test_parse_export_payload_rejects_negative_skipped_count(self):
        payload = json.dumps({"notes": [], "skipped": -1})

        with self.assertRaises(notes_cli.NotesExportError):
            notes_cli.parse_export_payload(payload)

    def test_parse_export_payload_rejects_empty_and_duplicate_note_ids(self):
        invalid_notes = [
            [{"id": "", "title": "Title", "body": "Body"}],
            [
                {"id": "duplicate", "title": "First", "body": "Body"},
                {"id": "duplicate", "title": "Second", "body": "Body"},
            ],
        ]

        for notes in invalid_notes:
            with self.subTest(notes=notes):
                payload = json.dumps({"notes": notes, "skipped": 0})
                with self.assertRaises(notes_cli.NotesExportError):
                    notes_cli.parse_export_payload(payload)

    def test_note_filename_is_stable_and_hides_note_id(self):
        note_id = "x-coredata://private-id"
        filename = notes_cli.note_filename(note_id)

        self.assertEqual(filename, notes_cli.note_filename(note_id))
        self.assertEqual(
            filename,
            f"{hashlib.sha256(note_id.encode('utf-8')).hexdigest()[:20]}.txt",
        )
        self.assertNotIn("private-id", filename)

    def test_write_export_replaces_stale_files_and_preserves_sibling_docs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            export_dir.mkdir(parents=True)
            (export_dir / "stale.txt").write_text("stale", encoding="utf-8")
            sibling_doc = root / "docs" / "keep.txt"
            sibling_doc.write_text("keep", encoding="utf-8")

            notes_cli.write_export(
                [notes_cli.AppleNote("1", "  Ideas  ", "  Build it  ")],
                export_dir,
            )

            exported_files = list(export_dir.glob("*.txt"))
            self.assertEqual(len(exported_files), 1)
            self.assertFalse((export_dir / "stale.txt").exists())
            self.assertEqual(sibling_doc.read_text(encoding="utf-8"), "keep")
            self.assertEqual(
                exported_files[0].read_text(encoding="utf-8"),
                "Title: Ideas\n\nBuild it\n",
            )

    def test_write_export_preserves_old_export_when_staging_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            export_dir.mkdir(parents=True)
            old_export = export_dir / "old.txt"
            old_export.write_text("old", encoding="utf-8")

            with patch.object(Path, "write_text", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    notes_cli.write_export(
                        [notes_cli.AppleNote("1", "Title", "Body")],
                        export_dir,
                    )

            self.assertEqual(old_export.read_text(encoding="utf-8"), "old")
            self.assertEqual(
                list(export_dir.parent.glob(".apple-notes-*")),
                [],
            )

    def test_write_export_restores_old_export_when_final_replace_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            export_dir.mkdir(parents=True)
            old_export = export_dir / "old.txt"
            old_export.write_text("old", encoding="utf-8")
            original_replace = Path.replace
            failed = False

            def fail_first_replace_to_export(source, target):
                nonlocal failed
                if target == export_dir and not failed:
                    failed = True
                    raise OSError("rename failed")
                return original_replace(source, target)

            with patch.object(Path, "replace", new=fail_first_replace_to_export):
                with self.assertRaisesRegex(OSError, "rename failed"):
                    notes_cli.write_export(
                        [notes_cli.AppleNote("1", "Title", "New body")],
                        export_dir,
                    )

            self.assertEqual(old_export.read_text(encoding="utf-8"), "old")
            self.assertEqual(
                list(export_dir.parent.glob(".apple-notes-*")),
                [],
            )


if __name__ == "__main__":
    unittest.main()
