import unittest
from logos_pipe_ocr.eval.schema_generator import JsonSchemaGenerator

class TestJsonSchemaGenerator(unittest.TestCase):
    def setUp(self):
        self.json_data = {
            "name": "John",
            "age": 30,
            "is_student": False,
            "courses": ["Math", "Science"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown"
            },
            "none_field": None
        }
        self.generator = JsonSchemaGenerator(self.json_data)

    def test_generate_json_schema(self):
        schema = self.generator.get_schema()
        self.assertEqual(schema["type"], "object")
        self.assertIn("name", schema["properties"])
        self.assertIn("age", schema["properties"])
        self.assertIn("is_student", schema["properties"])
        self.assertIn("courses", schema["properties"])
        self.assertIn("address", schema["properties"])
        self.assertEqual(schema["properties"]["name"]["type"], "string")
        self.assertEqual(schema["properties"]["age"]["type"], "integer")
        self.assertEqual(schema["properties"]["is_student"]["type"], "boolean")
        self.assertEqual(schema["properties"]["courses"]["type"], "array")
        self.assertEqual(schema["properties"]["address"]["type"], "object")
        self.assertEqual(schema["properties"]["address"]["properties"]["street"]["type"], "string")
        self.assertEqual(schema["properties"]["address"]["properties"]["city"]["type"], "string")
        self.assertEqual(schema["properties"]["courses"]["items"]["type"], "string")
        self.assertEqual(schema["properties"]["none_field"]["type"], "string")

    def test_required_fields(self):
        required_fields = self.generator.get_required_fields()
        self.assertEqual(len(required_fields), 6)  # 모든 필드가 필수로 설정됨

    def test_boolean_fields(self):
        boolean_fields = self.generator.get_boolean_fields()
        self.assertIn("is_student", boolean_fields)

if __name__ == "__main__":
    unittest.main()