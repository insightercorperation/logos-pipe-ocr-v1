import unittest
import os
import json

from logos_pipe_ocr.util.datahandlers import EvalDataHandler

class TestEvalDataHandler(unittest.TestCase):
    def setUp(self):
        # 테스트용 데이터 생성
        self.label_dir = 'test_labels'
        self.output_dir = 'test_outputs'
        os.makedirs(self.label_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # JSON 파일 생성
        with open(os.path.join(self.label_dir, 'test.json'), 'w') as f:
            json.dump({"key": "value"}, f)
        with open(os.path.join(self.output_dir, 'test.json'), 'w') as f:
            json.dump({"key": "output_value"}, f)

        # TXT 파일 생성
        with open(os.path.join(self.label_dir, 'test2.txt'), 'w') as f:
            f.write("This is a test label.")
        with open(os.path.join(self.output_dir, 'test2.txt'), 'w') as f:
            f.write("This is a test output.")

        self.handler = EvalDataHandler(self.label_dir, self.output_dir)

    def tearDown(self):
        # 테스트 후 데이터 삭제
        for file in os.listdir(self.label_dir):
            os.remove(os.path.join(self.label_dir, file))
        for file in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, file))
        os.rmdir(self.label_dir)
        os.rmdir(self.output_dir)

    def test_call_method(self):
        # __call__ 메소드 테스트
        eval_data = self.handler()
        self.assertIsInstance(eval_data, dict)
        self.assertIn("processed_data", eval_data)

    def test_len_method(self):
        # __len__ 메소드 테스트
        self.handler()  # 데이터 로드
        self.assertEqual(len(self.handler), len(self.handler.eval_data["processed_data"]))

    def test_get_label_data(self):
        # get_label_data 메소드 테스트
        self.handler()  # 데이터 로드
        labels = self.handler.get_label_data()
        self.assertIsInstance(labels, list)
        self.assertEqual(labels, ["This is a test label.", {"key": "value"}])

    def test_get_output_data(self):
        # get_output_data 메소드 테스트
        self.handler()  # 데이터 로드
        outputs = self.handler.get_output_data()
        self.assertIsInstance(outputs, list)
        self.assertEqual(outputs, ["This is a test output.", {"key": "output_value"}])

if __name__ == "__main__":
    unittest.main()