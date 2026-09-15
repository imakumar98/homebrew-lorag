import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import lorag.rag as rag


class AnswerQuestionTests(unittest.TestCase):
    def test_answer_question_requires_existing_index(self):
        with tempfile.TemporaryDirectory() as directory:
            db_dir = Path(directory) / "db"

            with self.assertRaisesRegex(
                rag.QuestionError,
                r"No index found\. Run `lorag sync`\.",
            ):
                rag.answer_question(
                    "What is ACATS?",
                    Path(directory) / "docs",
                    db_dir,
                    "nomic-embed-text",
                    "llama3.2:3b",
                )

    def test_answer_question_returns_answer_and_unique_sources(self):
        docs = [
            Mock(metadata={"source": "/tmp/a.txt"}),
            Mock(metadata={"source": "/tmp/a.txt"}),
            Mock(metadata={"source": "/tmp/b.txt"}),
        ]
        agent = Mock()
        agent.invoke.return_value = {
            "messages": [Mock(content="Fee is waived")],
            "context": docs,
        }

        vector_store = Mock()
        with (
            patch.object(rag, "get_vectorstore", return_value=vector_store) as get_vs,
            patch.object(rag, "build_agent", return_value=agent) as build,
            tempfile.TemporaryDirectory() as directory,
        ):
            db_dir = Path(directory) / "db"
            db_dir.mkdir()
            docs_dir = Path(directory) / "docs"

            answer, sources = rag.answer_question(
                "What is ACATS?",
                docs_dir,
                db_dir,
                "nomic-embed-text",
                "llama3.2:3b",
            )

        self.assertEqual(answer, "Fee is waived")
        self.assertEqual(sources, ["/tmp/a.txt", "/tmp/b.txt"])
        get_vs.assert_called_once_with(docs_dir, db_dir, "nomic-embed-text")
        build.assert_called_once_with(vector_store, "llama3.2:3b")
        agent.invoke.assert_called_once_with({
            "messages": [{"role": "user", "content": "What is ACATS?"}],
            "context": [],
        })

    def test_answer_question_maps_connection_refused_to_ollama_error(self):
        with (
            patch.object(
                rag,
                "get_vectorstore",
                side_effect=ConnectionError("connection refused"),
            ),
            patch.object(rag, "build_agent"),
            tempfile.TemporaryDirectory() as directory,
        ):
            db_dir = Path(directory) / "db"
            db_dir.mkdir()

            with self.assertRaisesRegex(
                rag.QuestionError,
                r"Ollama is not running\. Start Ollama and try again\.",
            ):
                rag.answer_question(
                    "What is ACATS?",
                    Path(directory) / "docs",
                    db_dir,
                    "nomic-embed-text",
                    "llama3.2:3b",
                )

    def test_answer_question_maps_model_not_found_to_missing_chat_model(self):
        agent = Mock()
        agent.invoke.side_effect = RuntimeError("model 'llama3.2:3b' not found")

        with (
            patch.object(rag, "get_vectorstore", return_value=Mock()),
            patch.object(rag, "build_agent", return_value=agent),
            tempfile.TemporaryDirectory() as directory,
        ):
            db_dir = Path(directory) / "db"
            db_dir.mkdir()

            with self.assertRaisesRegex(
                rag.QuestionError,
                r"Chat model is missing\. Run `lorag model use <name>`\.",
            ):
                rag.answer_question(
                    "What is ACATS?",
                    Path(directory) / "docs",
                    db_dir,
                    "nomic-embed-text",
                    "llama3.2:3b",
                )

    def test_answer_question_does_not_remap_unrelated_model_errors(self):
        with (
            patch.object(
                rag,
                "get_vectorstore",
                side_effect=RuntimeError("embedding model failed"),
            ),
            patch.object(rag, "build_agent"),
            tempfile.TemporaryDirectory() as directory,
        ):
            db_dir = Path(directory) / "db"
            db_dir.mkdir()

            with self.assertRaises(RuntimeError) as ctx:
                rag.answer_question(
                    "What is ACATS?",
                    Path(directory) / "docs",
                    db_dir,
                    "nomic-embed-text",
                    "llama3.2:3b",
                )

        self.assertNotIsInstance(ctx.exception, rag.QuestionError)
        self.assertEqual(str(ctx.exception), "embedding model failed")
