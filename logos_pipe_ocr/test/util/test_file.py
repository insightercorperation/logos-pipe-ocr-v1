import unittest
from logos_pipe_ocr.util.file import create_txt_file, create_json_file, read_json_file, read_txt_file, increment_path
import os
import json

class TestFileFunctions(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'test_dir'
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def test_create_txt_file(self):
        create_txt_file("Hello, World!", self.test_dir, "test")
        with open(os.path.join(self.test_dir, "test.txt"), 'r', encoding='utf-8-sig') as f:
            content = f.read()
        self.assertEqual(content, "Hello, World!")

        dict_list = [{"key1": "value1"}, {"key2": "value2"}]
        create_txt_file(str(dict_list), self.test_dir, "dict_list_test")
        with open(os.path.join(self.test_dir, "dict_list_test.txt"), 'r', encoding='utf-8-sig') as f:
            dict_list_content = f.read()
        self.assertEqual(dict_list_content, str(dict_list))

    def test_create_json_file(self):
        data = {"key": "value"}
        create_json_file(data, self.test_dir, "test")
        with open(os.path.join(self.test_dir, "test.json"), 'r', encoding='utf-8-sig') as f:
            content = json.load(f)
        self.assertEqual(content, data)
    
    def test_read_json_file(self):
        data = {"key": "value"}
        create_json_file(data, self.test_dir, "test")
        result = read_json_file(os.path.join(self.test_dir, "test.json"))
        self.assertEqual(result, data)

    def test_read_txt_file(self):
        dict_item = {"key1": "value1"}
        dict_list = [{"key1": "value1"}, {"key2": "value2"}]
        create_txt_file(str(dict_item), self.test_dir, "dict_item_test")
        create_txt_file(str(dict_list), self.test_dir, "dict_list_test")
        result_item = read_txt_file(os.path.join(self.test_dir, "dict_item_test.txt"))
        self.assertEqual(result_item, str(dict_item))
        result_list = read_txt_file(os.path.join(self.test_dir, "dict_list_test.txt"))
        self.assertEqual(result_list, str(dict_list))

    def test_increment_path(self):
        path = increment_path(os.path.join(self.test_dir, "test.txt"))
        self.assertTrue(path.name.startswith("test.txt"))

if __name__ == '__main__':
    unittest.main() 