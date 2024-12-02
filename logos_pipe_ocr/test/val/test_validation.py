import unittest
from logos_pipe_ocr.val.validation import Validation, FidelityValidation, TextValidation

class TestValidation(unittest.TestCase):
    
    def setUp(self):
        self.eval_metrics = ["accuracy", "cer", "wer"]  # 평가 지표 설정
        self.validation = Validation(self.eval_metrics)

    def test_fidelity_validation(self):
        processed_predicted_data = [{"key1": "value1", "key2": "value2", "file_name": "test1.png", "boolean_field": True}, {"key1": "value1", "key2": "value2", "file_name": "test2.png", "boolean_field": True}]
        processed_ground_truth_data = [{"key1": "value1", "key2": "value2", "file_name": "test1.png", "boolean_field": True}, {"key1": "value1", "key2": "value2", "file_name": "test2.png", "boolean_field": False}]
        
        results = self.validation.run("test.png", processed_predicted_data, processed_ground_truth_data)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 0)

    def test_text_validation(self):
        processed_predicted_data = [{"key1": "value1", "key2": "value2", "file_name": "test1.png"}, {"key1": "value1", "key2": "value2", "file_name": "test2.png"}]
        processed_ground_truth_data = [{"key1": "value1", "key2": "value2", "file_name": "test1.png"}, {"key1": "value1", "key2": "value2", "file_name": "test2.png"}]
        
        results = self.validation.run("test.png", processed_predicted_data, processed_ground_truth_data)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 0)

    def test_validation_with_missing_data(self):
        
        processed_predicted_data = [{"key1": "value1", "key2": "value2", "file_name": "test1.png"}]
        processed_ground_truth_data = [{"key1": "value1", "key2": "value2", "file_name": "test1.png", "boolean_field": True}, {"key1": "value1", "key2": "value2", "file_name": "test2.png"}]
        
        results = self.validation.run("test.png", processed_predicted_data, processed_ground_truth_data)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 0)

    def test_handle_missing_data(self):
        # 예외 상황 테스트
        with self.assertRaises(ValueError):
            self.validation._check_ground_truth_data([])

    def test_invalid_eval_metrics(self):
        self.invalid_eval_metrics = ["accuracy", "abc"]
        self.test_valid = Validation(self.invalid_eval_metrics)
        with self.assertRaises(ValueError):
            self.test_valid.run("test.png", [], [])

if __name__ == '__main__':
    unittest.main()