import unittest
from logos_pipe_ocr.util.datahandlers import EvalDataHandler

class TestEvalDataHandler(unittest.TestCase):
    def setUp(self):
        # 테스트를 위한 가짜 데이터 경로 설정
        self.label_dir_path = "../data/testset/textbook"
        self.output_dir_path = "../output/exp_result_gemini-1.5-pro2/preds"
        self.data_handler = EvalDataHandler(self.label_dir_path, self.output_dir_path)

    def test_call_method(self):
        # __call__ 메서드 테스트
        result = self.data_handler()
        self.assertIsInstance(result, dict)
        self.assertIn("processed_data", result)

    def test_len_method(self):
        # __len__ 메서드 테스트
        self.data_handler()
        self.assertEqual(len(self.data_handler), len(self.data_handler.eval_data["processed_data"]))

    def test_get_label_data(self):
        # get_label_data 메서드 테스트
        self.data_handler()
        labels = self.data_handler.get_label_data()
        self.assertIsInstance(labels, list)

    def test_get_output_data(self):
        # get_output_data 메서드 테스트
        self.data_handler()
        outputs = self.data_handler.get_output_data()
        self.assertIsInstance(outputs, list)

if __name__ == "__main__":
    unittest.main() 