import hashlib
import io
import json
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

    def test_project_defaults_are_relative_to_module(self):
        project_root = Path(notes_cli.__file__).resolve().parent

        self.assertEqual(notes_cli.DEFAULT_EXPORT_DIR, project_root / "docs" / "apple-notes")
        self.assertEqual(notes_cli.DEFAULT_DB_DIR, project_root / "db")

    def test_gitignore_protects_transaction_artifacts(self):
        project_root = Path(notes_cli.__file__).resolve().parent
        patterns = (project_root / ".gitignore").read_text(encoding="utf-8").splitlines()

        self.assertIn("docs/.apple-notes-*", patterns)
        self.assertIn("docs/.apple-notes-backup-*", patterns)
        self.assertIn(".db-staging-*", patterns)
        self.assertIn(".db-backup-*", patterns)

    def test_rebuild_index_wires_paths_to_main_module(self):
        fake_rag = types.ModuleType("main")
        fake_rag.get_vectorstore = Mock(return_value=object())
        docs_dir = Path("/tmp/project/docs")
        db_dir = Path("/tmp/project/db")

        with patch.dict(sys.modules, {"main": fake_rag}):
            notes_cli.rebuild_index(docs_dir, db_dir)

        self.assertEqual(fake_rag.DOCS_DIR, docs_dir)
        self.assertEqual(fake_rag.DB_DIR, db_dir)
        fake_rag.get_vectorstore.assert_called_once_with()

    def test_sync_builds_staging_then_swaps_existing_db(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            db_dir = root / "db"
            db_dir.mkdir()
            old_index = db_dir / "old-index"
            old_index.write_text("old", encoding="utf-8")
            notes = [notes_cli.AppleNote("1", "Private title", "Private body")]
            events = []

            def fetch():
                events.append("fetch")
                return notes, 2

            real_write_export = notes_cli.write_export

            def export(passed_notes, passed_export_dir):
                events.append("export")
                real_write_export(passed_notes, passed_export_dir)

            def rebuild(docs_dir, staging_db_dir):
                events.append(
                    (
                        "rebuild",
                        docs_dir,
                        staging_db_dir.parent,
                        staging_db_dir.name.startswith(".db-staging-"),
                        staging_db_dir.exists(),
                        old_index.exists(),
                    )
                )
                staging_db_dir.mkdir()
                (staging_db_dir / "new-index").write_text("new", encoding="utf-8")

            with patch("notes_cli.write_export", side_effect=export):
                exported, skipped = notes_cli.sync_notes(
                    export_dir,
                    db_dir,
                    fetch=fetch,
                    rebuild=rebuild,
                )

            self.assertEqual(
                events,
                [
                    "fetch",
                    "export",
                    ("rebuild", export_dir.parent, root, True, False, True),
                ],
            )
            self.assertEqual((exported, skipped), (1, 2))
            self.assertTrue(export_dir.exists())
            self.assertFalse(old_index.exists())
            self.assertEqual(
                (db_dir / "new-index").read_text(encoding="utf-8"),
                "new",
            )
            self.assertEqual(list(root.glob(".db-*")), [])

    def test_sync_preserves_existing_db_when_rebuild_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_dir = root / "db"
            db_dir.mkdir()
            old_index = db_dir / "old-index"
            old_index.write_text("old", encoding="utf-8")

            def fail_rebuild(_docs_dir, staging_db_dir):
                self.assertFalse(staging_db_dir.exists())
                staging_db_dir.mkdir()
                (staging_db_dir / "partial").write_text("partial", encoding="utf-8")
                raise RuntimeError("sensitive rebuild details")

            with self.assertRaisesRegex(
                notes_cli.NotesExportError,
                "^Notes were exported, but the index rebuild failed\\.$",
            ):
                notes_cli.sync_notes(
                    root / "docs" / "apple-notes",
                    db_dir,
                    fetch=Mock(return_value=([], 0)),
                    rebuild=fail_rebuild,
                )

            self.assertEqual(old_index.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(root.glob(".db-*")), [])

    def test_sync_restores_existing_db_when_final_swap_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_dir = root / "db"
            db_dir.mkdir()
            old_index = db_dir / "old-index"
            old_index.write_text("old", encoding="utf-8")
            original_replace = Path.replace

            def rebuild(_docs_dir, staging_db_dir):
                staging_db_dir.mkdir()
                (staging_db_dir / "new-index").write_text("new", encoding="utf-8")

            def fail_staging_swap(source, target):
                if source.name.startswith(".db-staging-") and target == db_dir:
                    raise OSError("sensitive rename details")
                return original_replace(source, target)

            with patch.object(Path, "replace", new=fail_staging_swap):
                with self.assertRaisesRegex(
                    notes_cli.NotesExportError,
                    "^Notes were exported, but the index rebuild failed\\.$",
                ):
                    notes_cli.sync_notes(
                        root / "docs" / "apple-notes",
                        db_dir,
                        fetch=Mock(return_value=([], 0)),
                        rebuild=rebuild,
                    )

            self.assertEqual(old_index.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(root.glob(".db-*")), [])

    def test_sync_promotes_staging_when_no_old_db_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_dir = root / "db"

            def rebuild(_docs_dir, staging_db_dir):
                self.assertFalse(db_dir.exists())
                self.assertFalse(staging_db_dir.exists())
                staging_db_dir.mkdir()
                (staging_db_dir / "new-index").write_text("new", encoding="utf-8")

            result = notes_cli.sync_notes(
                root / "docs" / "apple-notes",
                db_dir,
                fetch=Mock(return_value=([], 3)),
                rebuild=rebuild,
            )

            self.assertEqual(result, (0, 3))
            self.assertTrue((db_dir / "new-index").exists())
            self.assertEqual(list(root.glob(".db-*")), [])

    def test_sync_resolves_injected_defaults_at_call_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            db_dir = root / "db"

            def rebuild(_docs_dir, staging_db_dir):
                staging_db_dir.mkdir()

            with (
                patch("notes_cli.fetch_notes", return_value=([], 4)) as fetch,
                patch("notes_cli.rebuild_index", side_effect=rebuild) as rebuild_mock,
            ):
                result = notes_cli.sync_notes(export_dir, db_dir)

            self.assertEqual(result, (0, 4))
            fetch.assert_called_once_with()
            rebuild_mock.assert_called_once()

    def test_sync_preserves_db_when_fetch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_dir = root / "db"
            db_dir.mkdir()
            marker = db_dir / "keep"
            marker.write_text("old", encoding="utf-8")
            rebuild = Mock()

            with self.assertRaises(notes_cli.NotesExportError):
                notes_cli.sync_notes(
                    root / "docs" / "apple-notes",
                    db_dir,
                    fetch=Mock(side_effect=notes_cli.NotesExportError("safe failure")),
                    rebuild=rebuild,
                )

            self.assertTrue(marker.exists())
            rebuild.assert_not_called()

    def test_sync_preserves_db_when_export_staging_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_dir = root / "db"
            db_dir.mkdir()
            marker = db_dir / "keep"
            marker.write_text("old", encoding="utf-8")
            rebuild = Mock()

            with patch("notes_cli.write_export", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(
                    notes_cli.NotesExportError,
                    "^Apple Notes export failed\\.$",
                ):
                    notes_cli.sync_notes(
                        root / "docs" / "apple-notes",
                        db_dir,
                        fetch=Mock(return_value=([], 0)),
                        rebuild=rebuild,
                    )

            self.assertTrue(marker.exists())
            rebuild.assert_not_called()

    def test_sync_wraps_rebuild_failure_without_sensitive_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "docs" / "apple-notes"
            sensitive = "private embedding credentials"

            with self.assertRaises(notes_cli.NotesExportError) as caught:
                notes_cli.sync_notes(
                    export_dir,
                    root / "db",
                    fetch=Mock(
                        return_value=(
                            [notes_cli.AppleNote("1", "Secret title", "Secret body")],
                            0,
                        )
                    ),
                    rebuild=Mock(side_effect=RuntimeError(sensitive)),
                )

            self.assertEqual(
                str(caught.exception),
                "Notes were exported, but the index rebuild failed.",
            )
            self.assertNotIn(sensitive, str(caught.exception))
            self.assertTrue(export_dir.exists())
            self.assertFalse((root / "db").exists())
            self.assertEqual(list(root.glob(".db-*")), [])

    def test_main_sync_prints_only_safe_counts_and_status(self):
        stdout = io.StringIO()
        note_content = "Secret title and body"

        with patch("notes_cli.sync_notes", return_value=(4, 1)):
            with redirect_stdout(stdout):
                result = notes_cli.main(["sync"])

        self.assertEqual(result, 0)
        self.assertIn("4", stdout.getvalue())
        self.assertIn("1", stdout.getvalue())
        self.assertIn("index rebuilt", stdout.getvalue().lower())
        self.assertNotIn(note_content, stdout.getvalue())

    def test_main_reports_safe_error_to_stderr(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        safe_message = "Notes were exported, but the index rebuild failed."

        with patch(
            "notes_cli.sync_notes",
            side_effect=notes_cli.NotesExportError(safe_message),
        ):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = notes_cli.main(["sync"])

        self.assertEqual(result, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn(safe_message, stderr.getvalue())

    def test_main_requires_subcommand_and_supports_help(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, "2"):
                notes_cli.main([])

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            with self.assertRaisesRegex(SystemExit, "0"):
                notes_cli.main(["--help"])
        self.assertIn("sync", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
