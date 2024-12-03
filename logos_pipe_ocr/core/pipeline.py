import time
import os
from core.model import ChatGPTModel, GeminiModel
from eval.evaluation import Evaluation
from util.file_utils import save_json_file

# 상수 정의
IMAGE_EXTENSION = '.png'
OUTPUT_EXTENSION = '.json'

class logos_ocr_pipe:
    def __init__(self, model_name: str, task: str, config: dict):
        self.config = config
        self.task = task
        prompt_path = self.config["common"]["prompt_path"][self.task]
        self.operation_results = {}

        # 모델 인스턴스 생성
        if model_name.lower() not in self.config:
            raise ValueError(f"{model_name} is not a valid model name.")  # 유효하지 않은 모델 이름 처리
        
        self.model_config = self.config[model_name]
        
        if self.task not in self.model_config:
            raise ValueError(f"{self.task} is not a valid task for {model_name}.")  # 유효하지 않은 작업 처리
        
        self.task_config = self.model_config[self.task] # 작업 config 저장
        self.model = self._initialize_model(model_name, prompt_path)  # 모델 초기화 메서드 호출

        # 평가 인스턴스 생성
        self.evaluation_metrics = self.config["common"]["evaluation_metrics"][self.task]
        self.validation_schema = self.config["common"]["response_schemas"][self.task] # 평가 스키마 저장
        self.evaluator = Evaluation(self.validation_schema, self.evaluation_metrics)

    def __str__(self):
        return f"{self.model.model_name} 모델을 활용하여 가공한 {self.task} 데이터의 품질 평가를 수행합니다."
    
    def print_results(self, results, test_name):  # 결과 출력 메서드 추가
        print(f"----------------------------------")
        print(f"테스트 이름: {test_name}")  # 테스트 이름 출력
        txt_results = results["text_validation_results"]
        fid_results = results["fidelity_validation_results"]
        print(f"** 텍스트 검증 결과 **")
        for key, value in txt_results.items():
            print(f"  {key}'s average CER: {value['cer']:.2f}")
        print(f"** 프롬프트 충실도 검증 결과 **")
        print(f"  스키마 유효도: {fid_results['schema_validity_percentage']:.2f}%")
        print(f"  누락된 필드: {fid_results['missing_fields'] if fid_results['missing_fields'] else 'NaN'}")
        if self.evaluation_metrics.get("boolean") is not None:
            if test_name in self.evaluation_metrics["boolean"] or test_name == "최종 결과":  # boolean 검증 항목이 있으면 F1 점수 출력
                for key, value in fid_results["f1_score"].items():
                    print(f"  {key}'s f1 score: {value:.2f}")
        print(f"----------------------------------")
        print() 

    def print_operation_results(self):
        # 결과를 출력하기 전에 결과가 존재하는지 확인
        if self.task not in self.operation_results or "testset_results" not in self.operation_results[self.task]:
            print("결과가 존재하지 않습니다.")  # 결과가 없을 경우 메시지 출력
            return
        print(f"----------------------------------")
        print(f"{self.model.model_name} 모델의 {self.task} 데이터의 품질 평가 결과(평균)")
        print(f"----------------------------------")
        for test_name, results in self.operation_results[self.task]["testset_results"].items():
            self.print_results(results, test_name)  # 결과 출력 메서드 호출

        print(f"----------------------------------")
        print(f"최종 품질 평가 결과(가중 평균)")
        print(f"----------------------------------")
        # 최종 결과 출력
        final_results = self.operation_results[self.task]["eval_results"]
        self.print_results(final_results, "최종 결과")  # 최종 결과 출력

    def calculate_operation_results(self): # 각 테스트 셋 별 평균 계산
        self.operation_results[self.task]["testset_results"] = {
            key: self.evaluator.calculate_average_metrics(value["eval_results"])
            for key, value in self.operation_results.items() if key != self.task
        }
        self.operation_results[self.task]["eval_results"] = self.evaluator.calculate_average_metrics(self.operation_results[self.task]["testset_results"])

    def save_operation_results(self): # 실행 결과 저장
        file_name = f"{self.task}_operation_results_{self.model.model_name}_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time() + 9 * 3600))}"  # 한국 시간으로 변경
        file_path = os.path.join(self.config["common"]["operation_results_path"], file_name)
        save_json_file(self.operation_results, file_path)
        print(f"Success: {self.model.model_name} 모델을 활용하여 {self.task} 데이터의 품질 평가 수행이 완료되었습니다.")
        print(f"품질 평가 수행 결과는 {file_path}.json 파일에 저장되었습니다.")

    def run(self):
        testset_path = self.config["common"]["testset_path"][self.task]
        testset_dir_name = os.path.basename(os.path.dirname(testset_path)) 

        for root, dirs, files in os.walk(testset_path):  # 하위 디렉토리 포함
            parent_dir_name = os.path.basename(os.path.dirname(root))  # 상위 디렉토리 이름 가져오기
            
            if parent_dir_name and parent_dir_name not in self.operation_results and parent_dir_name != testset_dir_name:
                self.operation_results[parent_dir_name] = {}  # 상위 디렉토리 이름을 키로 하고 빈 딕셔너리 초기화
                self.operation_results[parent_dir_name]["tmpfile_paths"] = []  # 임시 파일 경로 리스트 초기화
                self.operation_results[parent_dir_name]["eval_results"] = []  # 평가 결과 리스트 초기화

            for file in files:
                if file.endswith(IMAGE_EXTENSION):  # 이미지 파일만 선택
                    test_image_path = os.path.join(root, file)  # 전체 경로 생성
                    json_file_name = os.path.splitext(file)[0] + OUTPUT_EXTENSION  # 파일 이름에서 확장자 변경
                    json_dir_path = os.path.join(os.path.dirname(root), "json")  # JSON 디렉토리 경로 생성
                    test_json_path = os.path.join(json_dir_path, json_file_name)  # JSON 경로 생성
                    temp_file_path = self.model.run(image_path=test_image_path)  # 모델의 run 메서드 호출
                    self.operation_results[parent_dir_name]["tmpfile_paths"].append(temp_file_path)  # 임시 파일 경로 리스트에 추가
                    # 각 파일에 대한 평가 결과를 새로 생성하여 저장
                    current_metric = self.evaluator.evaluate(temp_file_path, test_json_path)                    
                    self.operation_results[parent_dir_name]['eval_results'].extend(current_metric)

        self.calculate_operation_results()
        self.print_operation_results()
        self.save_operation_results()
        

        
