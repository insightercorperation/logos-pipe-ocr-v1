import unittest
from logos_pipe_ocr.core.evaluation import Evaluation

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        test_label_dir_path = "../data/test/label"
        test_output_dir_path = "../data/test/output"
        eval_metrics = ["accuracy", "cer", "wer", "cosine_similarity", "jaccard_similarity"]
        self.evaluator = Evaluation(test_label_dir_path, test_output_dir_path, eval_metrics)

    def test_run(self):
        results = self.evaluator.run()
        self.assertIsInstance(results, dict)  # 결과가 딕셔너리인지 확인

    def test_save(self):
        self.evaluator.evaluation_results = {"test_file": {"accuracy": 0.95}}
        self.evaluator.save("test_save_path", "test_file", "json")

    def test_calculate_average_metrics(self):
        eval_results = [{"accuracy": 0.9}, {"accuracy": 0.95}]
        average_metrics = self.evaluator.calculate_average_metrics(eval_results)
        self.assertIn("accuracy", average_metrics)  # 평균 메트릭스에 정확도가 포함되어 있는지 확인

if __name__ == "__main__":
    unittest.main()