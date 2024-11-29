import unittest
from logos_pipe_ocr.val.validation import TextValidation

class TestTextValidation(unittest.TestCase):
    def setUp(self):
        self.text_validator = TextValidation()
        self.text_validator.eval_metrics = ['accuracy', 'cer', 'wer'] # 텍스트 검증 메트릭 설정(자식 클래스 테스트 코드라 직접 설정)

    def test_run_with_valid_data(self):
        predicted_data = {"key": "value", "text": "hello world"}
        ground_truth_data = {"key": "value", "text": "hello wold"}
        results = self.text_validator.run(predicted_data, ground_truth_data)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_run_with_empty_ground_truth(self):
        predicted_data = {"key": "value"}
        ground_truth_data = {}
        with self.assertRaises(ValueError):
            self.text_validator.run(predicted_data, ground_truth_data)

    def test_run_with_missing_data(self):
        predicted_data = None  
        ground_truth_data = {"key1": "value1", "key2": "value2"}
        results = self.text_validator.run(predicted_data, ground_truth_data)
        print(results)
        self.assertEqual(results, [{'key1': {'accuracy': 0.0, 'cer': 1.0, 'wer': 1.0}, 'key2': {'accuracy': 0.0, 'cer': 1.0, 'wer': 1.0}}])

    def test_run_with_different_texts(self):
        predicted_data = {"key": "value", "text": "goodbye world"}
        ground_truth_data = {"key": "value", "text": "hello world"}
        results = self.text_validator.run(predicted_data, ground_truth_data)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

if __name__ == '__main__':
    unittest.main() 