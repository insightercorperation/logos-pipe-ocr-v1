from eval.preprocess import text_processing
from util.file_utils import read_json_file
from eval.calculate import calculate_testset_average_metrics, calculate_operation_average_metrics
from eval.validation import Validation

class Evaluation:
    def __init__(self, validation_schema: dict = None, evaluation_metrics: dict = None):
        self.validation_schema = validation_schema
        self.evaluation_metrics = evaluation_metrics
    
    def evaluate(self, temp_file_path: str, ground_truth_file_path: str) -> dict:  # 반환값을 dict로 변경
        self.file_name = None
        self.processed_predicted_data = []
        self.processed_ground_truth_data = []
        self.combined_results = []
        
        print("LLM 생성 데이터셋 검증을 시작합니다.")
        # 텍스트 파일 읽기
        predicted_data = read_json_file(temp_file_path)
        ground_truth_data = read_json_file(ground_truth_file_path)
        
        # 파일 이름 저장
        file_name = ground_truth_file_path.split("/")[-1].split(".")[0]

        self.processed_predicted_data = text_processing(predicted_data)
        self.processed_ground_truth_data = text_processing(ground_truth_data)

        # 검증 수행
        self.validator = Validation(file_name, self.validation_schema, self.processed_predicted_data, self.processed_ground_truth_data)
        self.combined_results = self.validator.validate()

        print("LLM 생성 데이터셋 검증을 완료했습니다.")
        return self.combined_results  # 통합된 결과 반환

    def calculate_average_metrics(self, eval_results: list[dict] | dict) -> dict: # 평균  계산
        try:    
            if isinstance(eval_results, list): # 테스트셋 평균 계산
                return calculate_testset_average_metrics(eval_results)
            elif isinstance(eval_results, dict): # 수행 결과 가중 평균 계산
                return calculate_operation_average_metrics(eval_results, self.evaluation_metrics)
        except ValueError as e:  
            raise ValueError(f"유효한 입력값이 아닙니다. {e}")

