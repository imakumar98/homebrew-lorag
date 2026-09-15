import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import lorag.rag as rag


def _doc(source: str, content: str = "") -> Mock:
    return Mock(metadata={"source": source}, page_content=content)


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
            _doc("/tmp/a.txt", "waived"),
            _doc("/tmp/a.txt", "also waived"),
            _doc("/tmp/b.txt", "other"),
        ]
        vector_store = Mock()
        vector_store.similarity_search.return_value = docs
        model = Mock()
        model.invoke.return_value = Mock(content="Fee is waived")

        with (
            patch.object(rag, "get_vectorstore", return_value=vector_store) as get_vs,
            patch.object(rag, "ChatOllama", return_value=model) as chat,
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
        chat.assert_called_once_with(
            model="llama3.2:3b",
            temperature=0,
            reasoning=False,
            num_predict=300,
        )
        vector_store.similarity_search.assert_called_once_with(
            "What is ACATS?",
            k=rag.RETRIEVAL_K,
        )
        messages = model.invoke.call_args.args[0]
        self.assertIn("waived", messages[0].content)
        self.assertIn("/tmp/a.txt", messages[0].content)
        self.assertEqual(messages[1].content, "What is ACATS?")

    def test_answer_question_maps_connection_refused_to_ollama_error(self):
        with (
            patch.object(
                rag,
                "get_vectorstore",
                side_effect=ConnectionError("connection refused"),
            ),
            patch.object(rag, "ChatOllama"),
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
        vector_store = Mock()
        vector_store.similarity_search.return_value = []
        model = Mock()
        model.invoke.side_effect = RuntimeError("model 'llama3.2:3b' not found")

        with (
            patch.object(rag, "get_vectorstore", return_value=vector_store),
            patch.object(rag, "ChatOllama", return_value=model),
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
            patch.object(rag, "ChatOllama"),
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
