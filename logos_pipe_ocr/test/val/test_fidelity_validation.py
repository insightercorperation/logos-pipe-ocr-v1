import unittest
from unittest.mock import patch, MagicMock
from logos_pipe_ocr.val.validation import FidelityValidation

class TestFidelityValidation(unittest.TestCase):
    def setUp(self):
        self.validator = FidelityValidation()

    @patch('logos_pipe_ocr.val.validation.JsonSchemaGenerator')
    def test_get_json_schema(self, MockJsonSchemaGenerator):
        # Mocking the JsonSchemaGenerator
        mock_generator = MockJsonSchemaGenerator.return_value
        mock_generator.schema = {"type": "object", "properties": {"key1": {"type": "string"}, "key2": {"type": "boolean"}}}
        mock_generator.required_fields = ["key1", "key2"]
        mock_generator.boolean_fields = ["key2"]

        processed_ground_truth_data = [
            {"key1": "value1", "key2": True},
            {"key1": "value2", "key2": False}
        ]
        
        self.validator._get_json_schema(processed_ground_truth_data)

        # Check if the schema is generated correctly
        self.assertEqual(self.validator.validation_schema, mock_generator.schema)
        self.assertEqual(self.validator.required_fields, mock_generator.required_fields)
        self.assertEqual(self.validator.boolean_fields, mock_generator.boolean_fields)

    def test_run_with_valid_data(self):
        processed_predicted_data = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"}
        ]
        processed_ground_truth_data = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"}
        ]

        results = self.validator.run(processed_predicted_data, processed_ground_truth_data)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result['schema_validity'] for result in results))

    def test_run_with_missing_data(self):
        processed_predicted_data = [
            {"key1": "value1"},
            None  # 두 번째 데이터가 없음
        ]
        processed_ground_truth_data = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"}
        ]

        results = self.validator.run(processed_predicted_data, processed_ground_truth_data)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertFalse(results[1]['schema_validity'])  # 정답에 비해 만들어진게 없으므로 다 0점인 결과가 나와야함
        self.assertIsNotNone(results[1]['missing_fields'])  # missing_fields가 None이 아닌지 확인

    def test_empty_ground_truth_data(self):
        with self.assertRaises(ValueError) as context:
            self.validator.run([], {})
        self.assertEqual(str(context.exception), "Ground truth data is empty. Cannot proceed with validation.")

    def test_run_with_empty_predicted_data(self):
        processed_predicted_data = []  # 예측 데이터가 비어있음
        processed_ground_truth_data = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"}
        ]

        results = self.validator.run(processed_predicted_data, processed_ground_truth_data)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertFalse(results[0]['schema_validity'])  # 첫 번째 데이터는 예측이 없으므로 유효성이 False여야 함
        self.assertIsNotNone(results[0]['missing_fields'])  # missing_fields가 None이 아닌지 확인

if __name__ == '__main__':
    unittest.main() 