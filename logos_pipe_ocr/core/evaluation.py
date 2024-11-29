"""
This module contains the core evaluator classes for the Logos-pipe-ocr project.
"""

from abc import ABC, abstractmethod
from logos_pipe_ocr.val.validation import Validation
from logos_pipe_ocr.util.datahandlers import EvalDataHandler
from logos_pipe_ocr.val.calculate import calculate_testset_average_metrics
from logos_pipe_ocr.util.file import save
from logos_pipe_ocr.val.text_processor import TextProcessor

class Evaluator(ABC):
    @abstractmethod
    def __init__(self, label_dir_path: str, output_dir_path: str, eval_metrics: str) -> None:
        self.label_dir_path = label_dir_path
        self.output_dir_path = output_dir_path
        self.eval_metrics = eval_metrics
        self.eval_data_handler = None
        self.validator = None
        self.evaluation_results = {}

    @abstractmethod
    def run(self) -> dict:
        pass    

    @abstractmethod
    def save(self, save_path: str, file_name: str, save_format) -> None:
        pass

class Evaluation(Evaluator):
    """ Evaluation class for evaluating the performance of the model.

    Args:
        label_dir_path (str): The path to the label directory.
        output_dir_path (str): The path to the output directory.
        eval_metrics (str): The evaluation metrics to use.
    
    Returns:
        eval_results (dict): A dictionary containing the evaluation results.
    """
    def __init__(self, label_dir_path: str, output_dir_path: str, eval_metrics: str) -> None:
        super().__init__(label_dir_path, output_dir_path, eval_metrics)
    
    def run(self) -> dict: 
        self.eval_data_handler = EvalDataHandler(self.label_dir_path, self.output_dir_path)
        self.validator = Validation(self.eval_metrics)
    
        for label_data, output_data in self.eval_data_handler:
            self.file_name = None
            
            # 파일 이름 저장
            self.file_name = label_data["file_name"]

            _processed_predicted_data, _processed_ground_truth_data = TextProcessor.run(output_data, label_data)

            self.validator.run(self.file_name, _processed_predicted_data, _processed_ground_truth_data)
            self.evaluation_results[self.file_name] = self.validator.validation_results
        
        print("Evaluation completed.")
        return self.evaluation_results  # 통합된 결과 반환
    
    def save(self, save_path: str, file_name: str = "", save_format: str = "json"):
        save(self.evaluation_results, save_path, file_name, save_format)
    
    def calculate_average_metrics(self, eval_results: list[dict] | dict) -> dict: # 평균  계산
        try:    
            return calculate_testset_average_metrics(eval_results)
        except ValueError as e:  
            raise ValueError(f"유효한 입력값이 아닙니다. {e}")