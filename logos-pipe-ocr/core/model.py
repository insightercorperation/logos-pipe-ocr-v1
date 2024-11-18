import os
import json
from PIL import Image
from io import BytesIO
from openai import OpenAI
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from src.utils.file_utils import read_prompt_file, create_temp_file

class ChatGPTModel:
    def __init__(self, model_config: dict, task_config: str, prompt_path: str):
        self.model_name = model_config["model_name"]
        self.task_config = task_config
        self.prompt = read_prompt_file(prompt_path)
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORGANIZATION"),
            project=os.environ.get("OPENAI_PROJECT"),
        )
        print(f"{self.model_name} 모델을 활용한 이미지 처리를 시작합니다.")
        
    def process_image(self, image_path: str) -> str:
        try:
            if not os.path.exists(image_path):  # 파일 존재 여부 확인
                print(f"파일이 존재하지 않습니다: {image_path}")
                return None
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"이미지 처리 오류: {e}")  # 이미지 처리 오류 추가

    def run(self, image_path: str) -> str:
        if not os.path.exists(image_path):  # 파일 존재 여부 확인
            print(f"파일이 존재하지 않습니다: {image_path}")
            return None
        print(f"{image_path} 이미지 분석을 수행합니다.")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self.process_image(image_path)}"}}
                        ]
                    }
                ],
                response_format = self.task_config["response_schemas"]
            )
            response_json = json.loads(response.choices[0].message.content)
            response_dict = response_json.get("items", response_json)

            if isinstance(response_dict, list):  # 리스트인지 확인
                for item in response_dict:
                    item["file_name"] = image_path.split("/")[-1]  # 권한 문제로 파일명 수동 추가
            else:
                response_dict["file_name"] = image_path.split("/")[-1]  # 권한 문제로 파일명 수동 추가
            
            temp_file_path = create_temp_file(response_dict, filename=os.path.basename(image_path))  # 임시 파일 생성
            return temp_file_path

        except json.JSONDecodeError as e:
            raise Exception(f"JSON 파싱 오류: {e}")  # JSON 파싱 오류 처리
        except Exception as e:
            raise Exception(f"오류 발생: {e}")  # 오류 발생 시 더 구체적인 메시지 추가

class GeminiModel:
    def __init__(self, model_config: dict, task_config: str, prompt_path: str):
        self.model_name = model_config["model_name"]
        self.prompt = read_prompt_file(prompt_path)
        vertexai.init(project=os.environ.get("VERTEXAI_PROJECT_ID"), location=os.environ.get("VERTEXAI_LOCATION"))
        self.gemini = GenerativeModel(
            model_name=self.model_name, 
            generation_config=GenerationConfig(
                seed=model_config["generation_config"]["seed"],
                response_mime_type=model_config["generation_config"]["response_mime_type"],
                response_schema=task_config["response_schemas"]) # 응답 스키마 정의
            )
        print(f"{self.model_name} 모델을 활용한 이미지 처리를 시작합니다.")

    def process_image(self, image_path: str) -> bytes:  # 단일 이미지 처리
        try:
            if not os.path.exists(image_path):  # 파일 존재 여부 확인
                print(f"파일이 존재하지 않습니다: {image_path}")
                return None
            with Image.open(image_path) as img:
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')
                return img_byte_arr.getvalue()
        except Exception as e:
            raise Exception(f"이미지 처리 오류: {e}")  # 이미지 처리 오류 추가

    def run(self, image_path: str) -> str:  # 여러 이미지 경로를 인자로 받음
        if not os.path.exists(image_path):  # 파일 존재 여부 확인
            print(f"파일이 존재하지 않습니다: {image_path}")
            return None
        print(f"{image_path} 이미지 분석을 수행합니다.")
        try:
            image_data = self.process_image(image_path)  # 여러 이미지 처리
            response = self.gemini.generate_content(
                [Part.from_data(image_data, mime_type="image/png"), Part.from_text(self.prompt)]
            )
            if response.candidates:
                response_json = json.loads(response.text)
                if isinstance(response_json, list):
                    for item in response_json:
                        item["file_name"] = image_path.split("/")[-1]  # 권한 문제로 파일명 수동 추가
                else:
                    response_json["file_name"] = image_path.split("/")[-1]  # 권한 문제로 파일명 수동 추가
                temp_file_path = create_temp_file(response_json, filename=os.path.basename(image_path))  # 임시 파일 생성
                return temp_file_path
            else:
                raise Exception(f"응답이 없습니다.")
        except Exception as e:
            raise Exception(f"오류 발생: {e}")  # 오류 처리 추가