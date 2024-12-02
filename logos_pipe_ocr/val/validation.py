from logos_pipe_ocr.val.fidelity import validate_json_schema, validate_judge_boolean
from logos_pipe_ocr.val.text_evaluator import TextEvaluator
from logos_pipe_ocr.val.schema_generator import JsonSchemaGenerator
from logos_pipe_ocr.util.file import save
from abc import ABC, abstractmethod

class Validator(ABC):
    @abstractmethod
    def __init__(self, eval_metrics: list[str]) -> None:
        self.eval_metrics = eval_metrics

    @abstractmethod
    def run(self, file_name: str, processed_predicted_data: list[dict] | dict, processed_ground_truth_data: list[dict] | dict) -> dict:
        pass

class Validation(Validator):
    """ Validation class for validating the performance of the model.

    Attributes:
        eval_metrics (str): The evaluation metrics to use.

    Returns:
        eval_results (dict): A dictionary containing the evaluation results.
    """
    def __init__(self, eval_metrics: list[str]) -> None:
        super().__init__(eval_metrics)
        self.validation_schema = None 
        self.fidelity_validator = None
        self.text_validator = None
        
    def __str__(self) -> str:
        result_str = (
            f"----------------------------------\n"
            f"** Evaluation Results **\n"
            f"----------------------------------\n"
            f" File Name: {self.file_name}\n"
            f"----------------------------------\n"
        )
        for result in self.validation_results:
            result_str += f" Prompt Fidelity Validation Results: {result['fidelity_validation_results']}\n"
            result_str += f" Text Validation Results: {result['text_validation_results']}\n"
            result_str += f"----------------------------------\n"
        return result_str
    
    def save(self, save_path: str, save_format: str) -> None:
        save(self.validation_results, save_path, save_format)   

    def run(self, file_name: str, processed_predicted_data: list[dict] | dict, processed_ground_truth_data: list[dict] | dict) -> dict: 
        self.validation_results = [] # initialize validation_results(it differs for each file)
        self.file_name = file_name
        self.validation_schema = self._get_json_schema(processed_ground_truth_data)
        self._initialize_validators()
        self._run_validators(processed_predicted_data, processed_ground_truth_data)
        self._create_combined_results()
        print(self)
        return self.validation_results

    def _initialize_validators(self) -> None:
        self.fidelity_validator = FidelityValidation(self.eval_metrics, self.validation_schema)
        self.text_validator = TextValidation(self.eval_metrics, self.validation_schema)

    def _run_validators(self, processed_predicted_data, processed_ground_truth_data) -> None:
        self._check_ground_truth_data(processed_ground_truth_data)
        self.fidelity_validator.run(processed_predicted_data, processed_ground_truth_data)
        self.text_validator.run(processed_predicted_data, processed_ground_truth_data)

    def _get_json_schema(self, processed_ground_truth_data: list[dict] | dict) -> JsonSchemaGenerator:
        _generator = JsonSchemaGenerator(processed_ground_truth_data)
        return _generator

    def _create_combined_results(self) -> None:
        for i in range(len(self.text_validator.text_validation_results)):
            self.validation_results.append({
                "file_name": self.file_name,
                "fidelity_validation_results": self.fidelity_validator.fidelity_validation_results[i],
                "text_validation_results": self.text_validator.text_validation_results[i] 
            })
    
    def _check_ground_truth_data(self, processed_ground_truth_data) -> None:
        if not processed_ground_truth_data:
            raise ValueError("Ground truth data is empty. Cannot proceed with validation.")

    def _validate_data(self, processed_predicted_data, processed_ground_truth_data, validate_function) -> None:
        if isinstance(processed_ground_truth_data, list):
            for i, ground_truth_data in enumerate(processed_ground_truth_data):
                if self._has_predicted_data(i):
                    predicted_data = processed_predicted_data[i]
                    validate_function(predicted_data, ground_truth_data)
                else:
                    self._handle_missing_data()
        else:
            if processed_predicted_data is not None:
                validate_function(processed_predicted_data, processed_ground_truth_data)
            else:
                self._handle_missing_data()
    
    def _has_predicted_data(self, index: int) -> bool:
        return index < len(self.processed_predicted_data) and self.processed_predicted_data[index] is not None

class FidelityValidation(Validation):
    """ FidelityValidation class for validating the fidelity of the model.

    Attributes:
        processed_predicted_data (list[dict] | dict): The processed predicted data.
    
    Returns:
        fidelity_validation_results (dict): A dictionary containing the fidelity validation results.
    """
    def __init__(self, eval_metrics: list[str], validation_schema: JsonSchemaGenerator) -> None:
        super().__init__(eval_metrics)
        self.processed_predicted_data = None
        self.processed_ground_truth_data = None
        self.schema = validation_schema.schema
        self.required_fields = validation_schema.required_fields
        self.boolean_fields = validation_schema.boolean_fields

    def run(self, processed_predicted_data: list[dict] | dict, processed_ground_truth_data: list[dict] | dict) -> dict:
        self.fidelity_validation_results = [] # initialize fidelity_validation_results(it differs for each file)
        self.processed_predicted_data = processed_predicted_data
        self.processed_ground_truth_data = processed_ground_truth_data
        self._validate_prompt_fidelity()
        return self.fidelity_validation_results

    def _validate_prompt_fidelity(self) -> None:
        self.schema_validity = None
        self.missing_fields = None  
        self.boolean_result = None  
        self._validate_data(self.processed_predicted_data, self.processed_ground_truth_data, self._validate_single_data_prompt_fidelity)

    def _validate_single_data_prompt_fidelity(self, predicted_data, ground_truth_data) -> None:
        prompt_fidelity_dict = {}
        self.schema_validity, self.missing_fields = validate_json_schema(predicted_data, self.schema)
        self.boolean_result = validate_judge_boolean(predicted_data, ground_truth_data)
        prompt_fidelity_dict["schema_validity"] = self.schema_validity
        prompt_fidelity_dict["missing_fields"] = self.missing_fields
        prompt_fidelity_dict["boolean_result"] = self.boolean_result
        self.fidelity_validation_results.append(prompt_fidelity_dict)
    
    def _handle_missing_data(self) -> None:
        # if there is no predicted data(list elements), create a data_valid_dict with False, missing_fields, and None
        self.fidelity_validation_results.append({"schema_validity": False, "missing_fields": self.required_fields, "boolean_result": None})
        print("WARNING: There is no generated data compared to the ground truth data.") # TODO: Need to set as exception?

class TextValidation(Validation):
    """ TextValidation class for validating the text detection performance of the model.

    Attributes:
        processed_predicted_data (list[dict] | dict): The processed predicted data.
    
    Returns:
        text_validation_results (list[dict]): A list of dictionaries containing the text validation results.
    """
    def __init__(self, eval_metrics: list[str], validation_schema: JsonSchemaGenerator) -> None:
        super().__init__(eval_metrics)
        self.processed_predicted_data = None
        self.processed_ground_truth_data = None
        self.boolean_fields = validation_schema.boolean_fields
        self.required_fields = validation_schema.required_fields
        self.evaluator = None

    def run(self, processed_predicted_data: list[dict] | dict, processed_ground_truth_data: list[dict] | dict) -> list[dict]:
        self.text_validation_results = [] # initialize text_validation_results(it differs for each file)
        self.processed_predicted_data = processed_predicted_data
        self.processed_ground_truth_data = processed_ground_truth_data
        self.evaluator = TextEvaluator(self.eval_metrics)
        self._validate_text_detection()
        return self.text_validation_results

    def _validate_text_detection(self) -> None:
        self._validate_data(self.processed_predicted_data, self.processed_ground_truth_data, self._validate_single_data_text_detection)

    def _validate_single_data_text_detection(self, predicted_data, ground_truth_data) -> None:  
        data_valid_dict = {}
        for field in ground_truth_data.keys():  
            if field == "file_name":
                continue
            elif field not in predicted_data.keys():  # if the key is not in predicted_data, can't calculate metrics
                print(f"WARNING: Can't calculate metrics. The key '{field}' is not in the predicted data. Please check the predicted data.")
                continue

            # predicted_data와 ground_truth_data의 값이 리스트인 경우
            predicted_text = predicted_data.get(field) if not isinstance(predicted_data.get(field), list) else predicted_data[field]
            ground_truth_text = ground_truth_data.get(field) if not isinstance(ground_truth_data.get(field), list) else ground_truth_data[field]

            evaluation_result = self.evaluator.run(predicted_text, ground_truth_text)
            if evaluation_result is not None:  
                data_valid_dict[field] = evaluation_result
        self.text_validation_results.append(data_valid_dict)  

    def _handle_missing_data(self) -> None: # TODO: Need to set as exception? 
        # if there is no predicted data(list elements), create a data_valid_dict with error_rate 1.0
        self.text_validation_results.append(self._create_data_valid_dict(self.required_fields))
        print("WARNING: There is no predicted data compared to the ground truth data. Please check the predicted data.")

    def _create_data_valid_dict(self, required_fields) -> dict:
        data_valid_dict = {}
        for field in required_fields:
            if field != "file_name" and field not in self.boolean_fields:
                data_valid_dict[field] = {metric: 0.0 if metric == "accuracy" else 1.0 for metric in self.eval_metrics}
        return data_valid_dict
    