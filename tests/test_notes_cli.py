import hashlib
import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

import notes_cli


class NoteExportTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
