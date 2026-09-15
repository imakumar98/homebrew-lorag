import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from lorag import cli
from lorag.paths import load_config


class LoragCliTests(unittest.TestCase):
    def test_init_creates_layout_and_runs_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            sync = Mock(return_value=(3, 1))
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(["init"], home=home, sync_notes=sync)

            paths = cli.paths_for(home)
            self.assertEqual(result, 0)
            self.assertTrue(paths.docs_dir.is_dir())
            self.assertTrue(paths.config_path.exists())
            self.assertEqual(load_config(paths).chat_model, "llama3.2:3b")
            sync.assert_called_once()
            args, kwargs = sync.call_args
            self.assertEqual(args[0], paths.notes_dir)
            self.assertEqual(args[1], paths.db_dir)

    def test_init_does_not_overwrite_chat_model(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            cli.main(["init"], home=home, sync_notes=Mock(return_value=(0, 0)))
            from lorag.paths import set_chat_model, LoragPaths

            set_chat_model(LoragPaths.from_home(home), "qwen3.5:4b")
            cli.main(["init"], home=home, sync_notes=Mock(return_value=(0, 0)))
            self.assertEqual(
                load_config(LoragPaths.from_home(home)).chat_model,
                "qwen3.5:4b",
            )

    def test_sync_reports_notes_error_to_stderr(self):
        from lorag.notes import NotesExportError

        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stderr(stderr):
                result = cli.main(
                    ["sync"],
                    home=Path(directory),
                    sync_notes=Mock(
                        side_effect=NotesExportError(
                            "Apple Notes sync is macOS-only."
                        )
                    ),
                )

        self.assertEqual(result, 1)
        self.assertIn("Apple Notes sync is macOS-only.", stderr.getvalue())

    def test_q_joins_remaining_args(self):
        stdout = io.StringIO()
        ask = Mock(return_value=("Fee is waived", ["/tmp/a.txt"]))
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            from lorag.paths import LoragPaths, ensure_layout, write_default_config

            paths = LoragPaths.from_home(home)
            ensure_layout(paths)
            write_default_config(paths)
            paths.db_dir.mkdir()

            with redirect_stdout(stdout):
                result = cli.main(
                    ["q", "What", "is", "ACATS?"],
                    home=home,
                    ask=ask,
                )

        self.assertEqual(result, 0)
        ask.assert_called_once()
        self.assertEqual(ask.call_args.args[0], "What is ACATS?")
        self.assertIn("Fee is waived", stdout.getvalue())
        self.assertIn("/tmp/a.txt", stdout.getvalue())

    def test_q_without_index_prints_helper_error(self):
        from lorag.rag import QuestionError

        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stderr(stderr):
                result = cli.main(
                    ["q", "hello"],
                    home=Path(directory),
                    ask=Mock(side_effect=QuestionError(
                        "No index found. Run `lorag init` or `lorag sync`."
                    )),
                )

        self.assertEqual(result, 1)
        self.assertIn("lorag init", stderr.getvalue())

    def test_q_without_query_is_an_error(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, "2"):
                cli.main(["q"])

    def test_model_prints_current_chat_model(self):
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            cli.main(["init"], home=home, sync_notes=Mock(return_value=(0, 0)))
            with redirect_stdout(stdout):
                result = cli.main(["model"], home=home)

        self.assertEqual(result, 0)
        self.assertIn("llama3.2:3b", stdout.getvalue())

    def test_model_use_saves_name_after_successful_pull(self):
        pull = Mock()
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            cli.main(["init"], home=home, sync_notes=Mock(return_value=(0, 0)))
            result = cli.main(
                ["model", "use", "qwen3.5:4b"],
                home=home,
                pull_model=pull,
            )
            self.assertEqual(result, 0)
            pull.assert_called_once_with("qwen3.5:4b")
            self.assertEqual(
                load_config(cli.paths_for(home)).chat_model,
                "qwen3.5:4b",
            )

    def test_model_use_does_not_save_when_pull_fails(self):
        pull = Mock(side_effect=cli.ModelPullError("pull failed"))
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            cli.main(["init"], home=home, sync_notes=Mock(return_value=(0, 0)))
            with redirect_stderr(stderr):
                result = cli.main(
                    ["model", "use", "missing:model"],
                    home=home,
                    pull_model=pull,
                )
            self.assertEqual(result, 1)
            self.assertEqual(
                load_config(cli.paths_for(home)).chat_model,
                "llama3.2:3b",
            )
