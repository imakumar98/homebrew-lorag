import tempfile
import unittest
from pathlib import Path

from sift.paths import (
    DEFAULT_CHAT_MODEL,
    DEFAULT_EMBED_MODEL,
    SiftPaths,
    ensure_layout,
    load_config,
    set_chat_model,
    write_default_config,
)


class SiftPathsTests(unittest.TestCase):
    def test_from_home_uses_visible_docs_and_hidden_state(self):
        home = Path("/tmp/fake-home")
        paths = SiftPaths.from_home(home)

        self.assertEqual(paths.docs_dir, home / "sift" / "docs")
        self.assertEqual(paths.db_dir, home / ".sift" / "db")
        self.assertEqual(paths.config_path, home / ".sift" / "config.toml")
        self.assertEqual(paths.notes_dir, home / "sift" / "docs" / "apple-notes")

    def test_ensure_layout_creates_docs_and_state_dirs(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = SiftPaths.from_home(Path(directory))

            ensure_layout(paths)

            self.assertTrue(paths.docs_dir.is_dir())
            self.assertTrue(paths.config_path.parent.is_dir())
            self.assertFalse(paths.db_dir.exists())

    def test_write_default_config_creates_expected_models(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = SiftPaths.from_home(Path(directory))
            ensure_layout(paths)

            write_default_config(paths)
            config = load_config(paths)

            self.assertEqual(config.chat_model, DEFAULT_CHAT_MODEL)
            self.assertEqual(config.embed_model, DEFAULT_EMBED_MODEL)
            self.assertEqual(DEFAULT_CHAT_MODEL, "llama3.2:3b")
            self.assertEqual(DEFAULT_EMBED_MODEL, "nomic-embed-text")

    def test_write_default_config_does_not_overwrite_existing_chat_model(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = SiftPaths.from_home(Path(directory))
            ensure_layout(paths)
            write_default_config(paths)
            set_chat_model(paths, "qwen3.5:4b")

            write_default_config(paths)

            self.assertEqual(load_config(paths).chat_model, "qwen3.5:4b")

    def test_load_config_returns_defaults_when_file_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = SiftPaths.from_home(Path(directory))

            config = load_config(paths)

            self.assertEqual(config.chat_model, "llama3.2:3b")
            self.assertEqual(config.embed_model, "nomic-embed-text")

    def test_set_chat_model_round_trips_quote_and_backslash(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = SiftPaths.from_home(Path(directory))
            ensure_layout(paths)
            write_default_config(paths)

            tricky = r'org/"custom\model"'
            set_chat_model(paths, tricky)

            config = load_config(paths)

            self.assertEqual(config.chat_model, tricky)
            self.assertEqual(config.embed_model, DEFAULT_EMBED_MODEL)
