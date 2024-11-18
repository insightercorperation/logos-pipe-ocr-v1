from eval.fidelity import validate_json_schema, validate_judge_boolean
from eval.metric import evaluate_text_detection

class Validation:
    def __init__(self, file_name: str, validation_schema: dict = None, processed_predicted_data: list[dict] | dict = None, processed_ground_truth_data: list[dict] | dict = None):
        self.file_name = file_name
        self.validation_schema = validation_schema
        self.required_fields = validation_schema['schema'].get("required", [])
        self.boolean_fields = {key: value for key, value in validation_schema['schema']['properties'].items() if value['type'] == 'boolean'}
        self.processed_predicted_data = processed_predicted_data
        self.processed_ground_truth_data = processed_ground_truth_data
        self.fidelity_validation_results = []
        self.text_validation_results = []
        self.combined_results = []

    def __str__(self) -> None:
        result_str = (
            f"----------------------------------\n"
            f"LLM 생성 데이터셋 검증 결과\n"
            f"----------------------------------\n"
            f"파일 이름: {self.file_name}\n"
        )
        for result in self.combined_results:
            result_str += f"프롬프트 충실도 검증 결과: {result['fidelity_validation_results']}\n"
            result_str += f"텍스트 검증 결과: {result['text_validation_results']}\n"
            result_str += f"----------------------------------\n"
        return result_str

    def validate_prompt_fidelity(self) -> None:
        try:
            self._validate_prompt_fidelity()
        except Exception as e:
            return f"프롬프트 충실도 검증 중 오류 발생: {e}"

    def _validate_prompt_fidelity(self) -> None:
        if isinstance(self.processed_ground_truth_data, list):
            for i, ground_truth_data in enumerate(self.processed_ground_truth_data):
                if self._has_predicted_data(i):
                    predicted_data = self.processed_predicted_data[i]
                    self._validate_single_data_prompt_fidelity(predicted_data, ground_truth_data)
                else:
                    self._handle_missing_data()
        else:
            if self.processed_predicted_data is not None:
                self._validate_single_data_prompt_fidelity(self.processed_predicted_data, self.processed_ground_truth_data)
            else:
                self._handle_missing_data()

    def _has_predicted_data(self, index: int) -> bool:
        return index < len(self.processed_predicted_data) and self.processed_predicted_data[index] is not None

    def _handle_missing_data(self) -> None:
        self.fidelity_validation_results.append({"schema_validity": False, "missing_fields": self.required_fields, "boolean_result": None})
        print("정답 데이터와 비교한 결과, 생성된 데이터가 없습니다.")

    def _validate_single_data_prompt_fidelity(self, predicted_data, ground_truth_data) -> None:
        self.schema_validity, self.missing_fields = validate_json_schema(predicted_data, self.validation_schema)
        self.boolean_result = validate_judge_boolean(predicted_data, ground_truth_data)
        self.fidelity_validation_results.append({
            "schema_validity": self.schema_validity, 
            "missing_fields": self.missing_fields, 
            "boolean_result": self.boolean_result
        })

    def validate_text_detection(self) -> None:
        try:    
            self._validate_text_detection()
            print("텍스트 검증 완료.")
        except Exception as e:
            return f"텍스트 검증 중 오류 발생: {e}"

    def _validate_text_detection(self) -> None:
        if isinstance(self.processed_ground_truth_data, list):
            for i, ground_truth_data in enumerate(self.processed_ground_truth_data):
                if self._has_predicted_data(i):
                    predicted_data = self.processed_predicted_data[i]
                    self._validate_single_data_text_detection(predicted_data, ground_truth_data)
                else:
                    self._handle_missing_data_text_detection(ground_truth_data)
        else:
            if self.processed_predicted_data is not None:
                self._validate_single_data_text_detection(self.processed_predicted_data, self.processed_ground_truth_data)
            else:
                self._handle_missing_data_text_detection(self.processed_ground_truth_data)

    def _handle_missing_data_text_detection(self, ground_truth_data) -> None:
        self.text_validation_results.append(self._create_data_valid_dict(ground_truth_data))
        print("정답 데이터와 비교한 결과, 생성된 데이터가 없습니다.")

    def _validate_single_data_text_detection(self, predicted_data, ground_truth_data) -> None:  
        data_valid_dict = {}
        for key in ground_truth_data.keys():  
            if key == "file_name":
                continue
            elif key not in predicted_data.keys():  
                data_valid_dict[key] = {"cer": 1.0}
                continue

            # predicted_data와 ground_truth_data의 값이 리스트인 경우
            predicted_text = predicted_data.get(key) if not isinstance(predicted_data.get(key), list) else predicted_data[key]
            ground_truth_text = ground_truth_data.get(key) if not isinstance(ground_truth_data.get(key), list) else ground_truth_data[key]

            evaluation_result = evaluate_text_detection(predicted_text, ground_truth_text)
            if evaluation_result is not None:  
                data_valid_dict[key] = evaluation_result
        self.text_validation_results.append(data_valid_dict)  

    def _create_data_valid_dict(self, ground_truth_data) -> dict:
        data_valid_dict = {}
        for key in ground_truth_data.keys():
            if key != "file_name" and key not in self.boolean_fields:
                data_valid_dict[key] = {"cer": 1.0}
        return data_valid_dict

    def validate(self):
        self.validate_prompt_fidelity()
        self.validate_text_detection()
        for i in range(len(self.text_validation_results)):
            self.combined_results.append({
                "file_name": self.file_name,
                "fidelity_validation_results": self.fidelity_validation_results[i],
                "text_validation_results": self.text_validation_results[i] 
            })
        print(self)
        return self.combined_results