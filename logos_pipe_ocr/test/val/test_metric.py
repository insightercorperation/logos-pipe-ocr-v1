import unittest
from logos_pipe_ocr.val.metric import accuracy, cer, wer, cosine_similarity, jaccard_similarity, average_metric, evaluate_text_detection

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

    def test_average_metric(self):
        metrics = {'accuracy': [1.0, 0.0], 'cer': [0.0, 0.2]}
        avg_result = average_metric(metrics)
        self.assertAlmostEqual(avg_result['accuracy'], 0.5)
        self.assertAlmostEqual(avg_result['cer'], 0.1)

    def test_evaluate_text_detection_with_lists(self):
        predicted_list = ["hello world", "goodbye world"]
        ground_truth_list = ["hello world", "goodbye everyone"]
        metrics = ['accuracy', 'cer', 'wer']
        
        result_list = evaluate_text_detection(predicted_list, ground_truth_list, metrics)
        
        self.assertAlmostEqual(result_list['accuracy'], 0.75)
        self.assertAlmostEqual(result_list['cer'], 0.21875)
        self.assertAlmostEqual(result_list['wer'], 0.5)
    
    def test_evaluate_text_detection_with_empty_lists(self):
        metrics = ['accuracy', 'cer', 'wer']
        result_list1 = evaluate_text_detection([], [], metrics)
        self.assertAlmostEqual(result_list1['accuracy'], 1.0)
        self.assertAlmostEqual(result_list1['cer'], 0.0)
        self.assertAlmostEqual(result_list1['wer'], 0.0)

        result_list2 = evaluate_text_detection(None, None, metrics)
        self.assertAlmostEqual(result_list2['accuracy'], 1.0)
        self.assertAlmostEqual(result_list2['cer'], 0.0)
        self.assertAlmostEqual(result_list2['wer'], 0.0)

        result_list3 = evaluate_text_detection(None, ["hello world"], metrics)
        self.assertAlmostEqual(result_list3['accuracy'], 0.0)
        self.assertAlmostEqual(result_list3['cer'], 1.0)
        self.assertAlmostEqual(result_list3['wer'], 1.0)

    def test_evaluate_text_detection_with_non_list_input(self):
        metrics = ['accuracy', 'cer', 'wer']
        with self.assertRaises(ValueError):
            evaluate_text_detection("hello world", ["goodbye world", "hello world"], metrics)

    def test_evaluate_text_detection_with_out_of_range_index(self):
        metrics = ['accuracy', 'cer', 'wer']
        with self.assertRaises(IndexError):
            evaluate_text_detection(["hello world", "goodbye world"], ["hello world", "goodbye everyone", "hello world"], metrics)
        with self.assertRaises(IndexError): 
            evaluate_text_detection(["hello world", "goodbye world", "hello world"], ["hello world", "goodbye everyone"], metrics)

    def test_evaluate_text_detection_with_invalid_metrics(self):
        predicted_list = ["hello world"]
        ground_truth_list = ["hello world"]
        invalid_metrics = ['invalid_metric']
        
        with self.assertRaises(ValueError):
            evaluate_text_detection(predicted_list, ground_truth_list, invalid_metrics)

if __name__ == '__main__':
    unittest.main()