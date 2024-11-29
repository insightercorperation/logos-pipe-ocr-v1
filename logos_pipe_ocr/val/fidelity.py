from jsonschema import Draft7Validator, validate

def validate_json_schema(processed_predicted_data: dict, validation_schema: dict) -> tuple[bool, list[str]]: # json schema 검증
    validator = Draft7Validator(validation_schema)
    errors = [error for error in validator.iter_errors(processed_predicted_data) if "additional properties" in error.message]
    
    missing_fields = []
    if errors:
        for error in errors:
            print(f"WARNING: {error.message}")
            missing_fields = [field for field in error.schema.get('required', []) if field not in processed_predicted_data]
            if missing_fields:
                print(f"WARNING: There are missing fields in the predicted data. (missing fields: {missing_fields})")
        return False, missing_fields
    else:
        print("INFO: All fields are validated successfully.")
        return True, None

def validate_judge_boolean(processed_predicted_data: dict, processed_ground_truth_data: dict) -> dict: # boolean 필드 검증
    boolean_result = {}
    for key, expected_value in processed_ground_truth_data.items():
        if isinstance(expected_value, bool): # boolean 타입인 경우
            predicted_value = processed_predicted_data.get(key)
            if predicted_value is not None:
                if expected_value != predicted_value:
                    print(f"WARNING: The value of the field '{key}' does not match. (predicted value: {predicted_value}, ground truth value: {expected_value})")
            boolean_result[key] = {"pred": predicted_value, "label": expected_value}
    print("INFO: All boolean fields are validated successfully.")
    return boolean_result

