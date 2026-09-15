import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import main as rag


class AnswerQuestionTests(unittest.TestCase):
    def test_answer_question_requires_existing_index(self):
        with tempfile.TemporaryDirectory() as directory:
            db_dir = Path(directory) / "db"

            with self.assertRaisesRegex(
                rag.QuestionError,
                r"No index found\. Run `sift init` or `sift sync`\.",
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

        with (
            patch.object(rag, "get_vectorstore", return_value=Mock()) as get_vs,
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
        build.assert_called_once()
        agent.invoke.assert_called_once_with({
            "messages": [{"role": "user", "content": "What is ACATS?"}],
            "context": [],
        })
