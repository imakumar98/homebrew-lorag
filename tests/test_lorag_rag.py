import unittest

from lorag.rag import BatchedEmbeddings


class RecordingEmbeddings:
    def __init__(self, *, fail_times=0):
        self.calls = []
        self.fail_times = fail_times

    def embed_documents(self, texts):
        self.calls.append(list(texts))
        if self.fail_times > 0:
            self.fail_times -= 1
            raise RuntimeError("tokenize EOF")
        return [[float(len(text))] for text in texts]

    def embed_query(self, text):
        return [float(len(text))]


class BatchedEmbeddingsTests(unittest.TestCase):
    def test_embed_documents_splits_into_batches(self):
        inner = RecordingEmbeddings()
        embeddings = BatchedEmbeddings(inner, batch_size=2)

        vectors = embeddings.embed_documents(["a", "bb", "ccc", "dddd", "e"])

        self.assertEqual(inner.calls, [["a", "bb"], ["ccc", "dddd"], ["e"]])
        self.assertEqual(vectors, [[1.0], [2.0], [3.0], [4.0], [1.0]])

    def test_embed_documents_retries_a_failed_batch(self):
        inner = RecordingEmbeddings(fail_times=1)
        embeddings = BatchedEmbeddings(inner, batch_size=2)

        vectors = embeddings.embed_documents(["a", "b"])

        self.assertEqual(inner.calls, [["a", "b"], ["a", "b"]])
        self.assertEqual(vectors, [[1.0], [1.0]])
