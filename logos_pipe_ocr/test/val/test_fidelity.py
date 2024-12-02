import unittest
from logos_pipe_ocr.val.fidelity import validate_json_schema, validate_judge_boolean

class TestFidelityFunctions(unittest.TestCase):

    def test_validate_json_schema(self):
        # 테스트 데이터
        processed_predicted_data = {"field1": "value1"}
        validation_schema = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "string"}
            },
            "required": ["field1", "field2"]
        }
        result = validate_json_schema(processed_predicted_data, validation_schema)
        self.assertFalse(result[0])  # False가 반환되어야 함
        self.assertIn("field2", result[1])  # 누락된 필드가 field2여야 함

    def test_validate_judge_boolean(self):
        # 테스트 데이터
        processed_predicted_data = {"key1": True, "key2": False}
        processed_ground_truth_data = {"key1": True, "key2": False}
        result = validate_judge_boolean(processed_predicted_data, processed_ground_truth_data)
        self.assertEqual(result["key1"]["pred"], True)  # 예측 값이 True여야 함
        self.assertEqual(result["key2"]["pred"], False)  # 예측 값이 False여야 함

    def test_validate_judge_boolean_with_missing_field(self):
        processed_predicted_data = {"key1": True}
        processed_ground_truth_data = {"key1": True, "key2": True}
        result = validate_judge_boolean(processed_predicted_data, processed_ground_truth_data)
        self.assertEqual(result["key2"]["pred"], None)  # 예측 값이 None여야 함
    
    def test_validate_judge_boolean_with_nan(self):
        processed_predicted_data = {"key1": True, "key2": None}
        processed_ground_truth_data = {"key1": True, "key2": True}
        result = validate_judge_boolean(processed_predicted_data, processed_ground_truth_data)
        self.assertEqual(result["key2"]["pred"], None)  # 예측 값이 None여야 함

if __name__ == '__main__':
    unittest.main() 