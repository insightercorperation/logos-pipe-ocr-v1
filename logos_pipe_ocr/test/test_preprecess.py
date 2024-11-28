import unittest
from logos_pipe_ocr.eval.preprocess import (
    convert_to_string,
    convert_choice,
    remove_extra_spaces,
    remove_all_whitespace,
    remove_special_characters_with_equation,
    normalize_string,
    text_processing,
)

class TestTextProcessing(unittest.TestCase):

    def setUp(self):
        # 테스트 데이터 설정
        self.test_data_dict = {
            "file_name": "test_file",
            "content": "이것은 테스트입니다! ① ② ③ $E=mc^2$ @#%&*()"
        }
        
        self.test_data_list = [
            {"file_name": "test_file_1", "content": "첫 번째 테스트입니다! ① ② $x+y=10$"},
            {"file_name": "test_file_2", "content": "두 번째 테스트입니다! ③ ④ @#%&*()"}
        ]
        
        self.test_data_dict_list = [
            {"file_name": "test_file_3", "content": "세 번째 테스트입니다! ⑤ $a^2 + b^2 = c^2$"},
            {"file_name": "test_file_4", "content": "네 번째 테스트입니다! ① ② ③ @#%&*()"}
        ]

    def test_convert_to_string(self):
        self.assertEqual(convert_to_string(123), "123")
        self.assertEqual(convert_to_string(45.67), "45.67")
        self.assertEqual(convert_to_string("test"), "test")

    def test_convert_choice(self):
        self.assertEqual(convert_choice("선택지: ①, ②, ③"), "선택지: 1, 2, 3")

    def test_remove_extra_spaces(self):
        self.assertEqual(remove_extra_spaces("  Hello   World  "), "Hello World")

    def test_remove_all_whitespace(self):
        self.assertEqual(remove_all_whitespace("Hello \n World\t!"), "Hello  World!")

    def test_remove_special_characters_with_equation(self):
        self.assertEqual(remove_special_characters_with_equation("이것은 $x + y$ 입니다!"), "이것은 x + y 입니다!")

    def test_normalize_string(self):
        self.assertEqual(normalize_string("Hello World"), "hello world")

    def test_text_processing_single_dict(self):
        input_data = {"file_name": "test.txt", "content": "  Hello   World  "}
        expected_output = {"file_name": "test.txt", "content": "hello world"}
        self.assertEqual(text_processing(input_data), expected_output)

    def test_text_processing_list(self):
        input_data = [
            {"file_name": "test1.txt", "content": "  Hello   World  "},
            {"file_name": "test2.txt", "content": "  Python   Programming  "}
        ]
        expected_output = [
            {"file_name": "test1.txt", "content": "hello world"},
            {"file_name": "test2.txt", "content": "python programming"}
        ]
        self.assertEqual(text_processing(input_data), expected_output)

    def test_text_processing_dict_with_list_values(self):
        input_data = {
            "file_name": "test.txt",
            "contents": [
                "  Hello   World  ",
                "  Python   Programming  "
            ]
        }
        expected_output = {
            "file_name": "test.txt",
            "contents": [
                "hello world",
                "python programming"
            ]
        }
        self.assertEqual(text_processing(input_data), expected_output)

    def test_process_single_dict(self):
        processed = text_processing(self.test_data_dict)
        self.assertIn("content", processed)
        self.assertEqual(processed["content"], "이것은 테스트입니다! 1 2 3 e=mc^2 #*()")

    def test_process_list_of_dicts(self):
        processed = text_processing(self.test_data_list)
        self.assertEqual(len(processed), 2)
        self.assertEqual(processed[0]["content"], "첫 번째 테스트입니다! 1 2 x+y=10")
        self.assertEqual(processed[1]["content"], "두 번째 테스트입니다! 3 4 #*()")

    def test_process_dict_of_lists(self):
        processed = text_processing(self.test_data_dict_list)
        self.assertEqual(len(processed), 2)
        self.assertEqual(processed[0]["content"], "세 번째 테스트입니다! 5 a^2 + b^2 = c^2")
        self.assertEqual(processed[1]["content"], "네 번째 테스트입니다! 1 2 3 #*()")

if __name__ == '__main__':
    unittest.main()