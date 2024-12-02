import unittest
from logos_pipe_ocr.val.text_evaluator import TextEvaluator

class TestTextEvaluator(unittest.TestCase):
    def setUp(self):
        metrics = ['accuracy', 'cer', 'wer']
        self.evaluator = TextEvaluator(metrics)

    def test_average_metric(self):
        metrics = {'accuracy': [1.0, 0.0], 'cer': [0.0, 0.2]}
        avg_result = self.evaluator._average_metric(metrics)
        self.assertAlmostEqual(avg_result['accuracy'], 0.5)
        self.assertAlmostEqual(avg_result['cer'], 0.1)

    def test_evaluate_text_detection_with_lists(self):
        predicted_list = ["hello world", "goodbye world"]
        ground_truth_list = ["hello world", "goodbye everyone"]
        
        result_list = self.evaluator.run(predicted_list, ground_truth_list)
        
        self.assertAlmostEqual(result_list['accuracy'], 0.75)
        self.assertAlmostEqual(result_list['cer'], 0.21875)
        self.assertAlmostEqual(result_list['wer'], 0.5)

    def test_check_type_validity_same_type(self):
        result = self.evaluator._check_type_validity("text", "another text")
        self.assertTrue(result)

    def test_check_type_validity_different_type(self):
        with self.assertRaises(ValueError):
            self.evaluator._check_type_validity("text", ["list", "of", "texts"])

    def test_check_metric_validity_valid_metric(self):
        result = self.evaluator._check_metric_validity(["accuracy"])
        self.assertTrue(result)

    def test_check_metric_validity_invalid_metric(self):
        with self.assertRaises(ValueError):
            self.evaluator._check_metric_validity(["invalid_metric"])
            
    def test_evaluate_text_detection_with_empty_lists(self):
        result_list1 = self.evaluator.run([], [])
        self.assertAlmostEqual(result_list1['accuracy'], 1.0)
        self.assertAlmostEqual(result_list1['cer'], 0.0)
        self.assertAlmostEqual(result_list1['wer'], 0.0)

        result_list2 = self.evaluator.run(None, None)
        self.assertAlmostEqual(result_list2['accuracy'], 1.0)
        self.assertAlmostEqual(result_list2['cer'], 0.0)
        self.assertAlmostEqual(result_list2['wer'], 0.0)

        result_list3 = self.evaluator.run(None, ["hello world"])
        self.assertAlmostEqual(result_list3['accuracy'], 0.0)
        self.assertAlmostEqual(result_list3['cer'], 1.0)
        self.assertAlmostEqual(result_list3['wer'], 1.0)

        result_list4 = self.evaluator.run("", None)
        self.assertAlmostEqual(result_list4['accuracy'], 1.0)
        self.assertAlmostEqual(result_list4['cer'], 0.0)
        self.assertAlmostEqual(result_list4['wer'], 0.0)

    def test_evaluate_text_detection_with_non_list_input(self):
        with self.assertRaises(ValueError):
            self.evaluator.run("hello world", ["goodbye world", "hello world"])

    def test_evaluate_text_detection_with_out_of_range_index(self):
        with self.assertRaises(IndexError):
            self.evaluator.run(["hello world", "goodbye world"], ["hello world", "goodbye everyone", "hello world"])
        with self.assertRaises(IndexError): 
            self.evaluator.run(["hello world", "goodbye world", "hello world"], ["hello world", "goodbye everyone"])

    def test_evaluate_text_detection_with_invalid_metrics(self):
        predicted_list = ["hello world"]
        ground_truth_list = ["hello world"]
        invalid_metrics = ['invalid_metric']
        self.evaluator.metrics = invalid_metrics
        with self.assertRaises(ValueError):
            self.evaluator.run(predicted_list, ground_truth_list)

if __name__ == '__main__':
    unittest.main()