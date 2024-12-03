import unittest
from unittest.mock import MagicMock, patch
from openai import OpenAI
import google.generativeai as genai
from logos_pipe_ocr.core.model import load_model, ChatGPTModel, GeminiModel
from logos_pipe_ocr.util.datahandlers import ChatGPTImageProcessor, ChatGPTResponseHandler, GeminiImageProcessor, GeminiResponseHandler
from logos_pipe_ocr.util.dataloaders import ImageLoader
from pathlib import Path
import os
from dotenv import load_dotenv

class TestModelLoading(unittest.TestCase):
    def test_load_chatgpt_model(self):
        config_file_path = './data/model_config/config.yaml'
        model = load_model('openai::gpt-4o-mini', model_config_path=config_file_path)
        self.assertIsInstance(model, ChatGPTModel)

    def test_load_gemini_model(self):
        model = load_model('google::gemini-1.5-pro', top_k=10, top_p=0.9)
        self.assertIsInstance(model, GeminiModel)

    def test_invalid_model(self):
        with self.assertRaises(ValueError):
            load_model('invalid::model-name')

    def test_empty_config_file(self):
        open(os.path.join('./data/model_config', 'empty_config.json'), 'wb').close()  # 빈 파일 생성

        with self.assertRaises(ValueError):
            load_model('openai::gpt-4o-mini', model_config_path='./data/model_config/empty_config.json')

        os.remove(os.path.join('./data/model_config', 'empty_config.json'))  # 빈 파일 삭제

    def test_model_config(self):
        config_path = "./data/model_config/config.json"
        model = load_model('google::gemini-1.5-pro', model_config_path=config_path, top_k=10, top_p=0.9)
        config = model._kwargs
        self.assertEqual(config['top_k'], 10)
        self.assertEqual(config['top_p'], 0.9)
        self.assertEqual(config['max_tokens'], 100)
        self.assertEqual(config['temperature'], 0.7)
        self.assertEqual(config['seed'], 42)
        self.assertEqual(config['repeat_penalty'], 1.2)
        self.assertIsInstance(model, GeminiModel)

class TestChatGPTModel(unittest.TestCase):
    def setUp(self):
        # 초기화 코드
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = "gpt-4o-mini"
        self.image_processor = ChatGPTImageProcessor()
        self.response_handler = ChatGPTResponseHandler()
        self.model_config = {}

        # 클라이언트 초기화 추가
        self.model = ChatGPTModel(self.api_key, self.model_name, self.image_processor, self.response_handler, self.model_config)
        self.model._client = OpenAI(api_key=self.api_key) # 클라이언트 모의 객체 설정

        self.prompt_path = "./data/prompt/prompt.txt"
        self.image_path = "./data/image"
        self.image_loader, self.prompt, self.save_dir = self.model._initialize_run(self.prompt_path, self.image_path, name="test_gpt", save_path="./data/runs")
    
    def test_initialize_run(self):
        self.assertIsInstance(self.image_loader, ImageLoader)
        self.assertIsInstance(self.prompt, str)
        self.assertIsInstance(self.save_dir, Path)

    def test_process_images(self):
        response_dict = self.model._process_images(self.image_loader, self.prompt, save_result=True, save_dir=self.save_dir, save_format="json")
        self.assertIsInstance(response_dict, dict) # _handle_response 결과 검증
        # _save_response 결과 검증
        self.assertEqual(os.path.exists(self.save_dir / "preds"), True) # preds 폴더가 존재하는지 확인
        self.assertEqual(os.path.exists(self.save_dir / "preds" / "dog" / "dog001.json"), True) # 폴더안에 데이터가 있는지 확인

    def test_generate_response(self):
        image_path = "./data/image/cat/cat001.jpeg"
        encoded_image = self.image_processor.process_image(image_path)
        response = self.model._generate_response(encoded_image, self.prompt)
        
        # 응답 검증
        self.assertIsNotNone(response)

class TestGeminiModel(unittest.TestCase):
    def setUp(self):
         # 초기화 코드
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-pro"
        self.image_processor = GeminiImageProcessor()
        self.response_handler = GeminiResponseHandler()
        self.model_config = {}

        # 클라이언트 초기화 추가
        self.model = GeminiModel(self.api_key, self.model_name, self.image_processor, self.response_handler, self.model_config)
        genai.configure(api_key=self.api_key)
        self.model._gemini = genai.GenerativeModel(model_name=self.model_name)

        self.prompt_path = "./data/prompt/prompt.txt"
        self.image_path = "./data/image"
        self.image_loader, self.prompt, self.save_dir = self.model._initialize_run(self.prompt_path, self.image_path, name="test_gpt", save_path="./data/runs")

    def test_initialize_run(self):
        self.assertIsInstance(self.image_loader, ImageLoader)
        self.assertIsInstance(self.prompt, str)
        self.assertIsInstance(self.save_dir, Path)

    def test_process_images(self):
        response_dict = self.model._process_images(self.image_loader, self.prompt, save_result=True, save_dir=self.save_dir, save_format="json")
        self.assertIsInstance(response_dict, dict) # _handle_response 결과 검증
        # _save_response 결과 검증
        self.assertEqual(os.path.exists(self.save_dir / "preds"), True) # preds 폴더가 존재하는지 확인
        self.assertEqual(os.path.exists(self.save_dir / "preds" / "dog" / "dog002.json"), True) # 폴더안에 데이터가 있는지 확인

    def test_generate_response(self):
        image_path = "./data/image/cat/cat002.jpeg"
        encoded_image = self.image_processor.process_image(image_path)
        response = self.model._generate_response(encoded_image, self.prompt)
        
        # 응답 검증
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()