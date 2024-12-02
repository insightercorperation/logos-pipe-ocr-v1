import unittest
from logos_pipe_ocr.val.metric import accuracy, cer, wer, cosine_similarity, jaccard_similarity

class TestMetrics(unittest.TestCase):
    def test_accuracy(self):
        self.assertAlmostEqual(accuracy("hello", "hello"), 1.0)
        self.assertAlmostEqual(accuracy("hello", "world"), 0.2)

    def test_cer(self):
        self.assertAlmostEqual(cer("hello", "hello"), 0.0)
        self.assertAlmostEqual(cer("hello", "hallo"), 0.2)

    def test_wer(self):
        self.assertAlmostEqual(wer("hello world", "hello world"), 0.0)
        self.assertAlmostEqual(wer("hello", "world"), 1.0)

    def test_cosine_similarity(self):
        self.assertAlmostEqual(cosine_similarity("hello", "hello"), 1.0)
        self.assertAlmostEqual(cosine_similarity("hello", "world"), 0.0)

    def test_jaccard_similarity(self):
        self.assertAlmostEqual(jaccard_similarity("hello world", "hello world"), 1.0)
        self.assertAlmostEqual(jaccard_similarity("hello", "world"), 0.0)

if __name__ == '__main__':
    unittest.main()