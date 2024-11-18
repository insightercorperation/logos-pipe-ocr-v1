from jsonschema import Draft7Validator
import logging

def validate_json_schema(processed_predicted_data: dict, validation_schema: dict) -> tuple[bool, list[str]]: # json schema 검증
    validator = Draft7Validator(validation_schema)
    errors = [error for error in validator.iter_errors(processed_predicted_data) if "additional properties" in error.message]
    
    missing_fields = []
    if errors:
        for error in errors:
            logging.error(f"json schema 검증 오류: {error.message}")
            missing_fields = [field for field in error.schema.get('required', []) if field not in processed_predicted_data]
            if missing_fields:
                logging.error(f"json schema 검증 오류: 누락된 필드: {missing_fields}")
        return False, missing_fields
    else:
        logging.info("json schema 검증 완료: 모든 필드가 정상적으로 생성되었습니다.")
        return True, None

def validate_judge_boolean(processed_predicted_data: dict, processed_ground_truth_data: dict) -> dict: # boolean 필드 검증
    boolean_result = {}
    for key, expected_value in processed_ground_truth_data.items():
        if isinstance(expected_value, bool): # boolean 타입인 경우
            predicted_value = processed_predicted_data.get(key)
            if predicted_value is not None:
                if expected_value != predicted_value:
                    logging.error(f"'boolean 필드 검증 오류: {key}' 필드의 값이 일치하지 않습니다. 예측값: {predicted_value}, 실제값: {expected_value}")
            boolean_result[key] = {"pred": predicted_value, "label": expected_value}
    logging.info("boolean 필드 검증 완료.")
    return boolean_result

