"""
This module contains the core model classes for the Logos-pipe-ocr project.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from openai import OpenAI
import google.generativeai as genai
from google.generativeai import GenerationConfig
from logos_pipe_ocr.util.file import increment_path
from logos_pipe_ocr.util.datahandlers import *
from logos_pipe_ocr.util.dataloaders import ImageLoader, PromptLoader, ModelConfigLoader

FILE_DIR = Path(__file__).resolve()
ROOT = FILE_DIR.parents[1]

class Model(ABC): 
    def __init__(self, api_key: str, model_name: str, image_processor: ImageProcessor, response_handler: ResponseHandler, model_config: dict) -> None:
        self._model = model_name
        self._api_key = api_key
        self.response_handler = response_handler
        self.image_processor = image_processor
        self._kwargs = model_config
        
    def _initialize_run(self, prompt_path: str, image_path: str, name: str, save_path: str) -> tuple[ImageLoader, str, Path]:
        image_loader = ImageLoader(image_path)
        prompt = PromptLoader(prompt_path).get_prompt()

        # Save directory
        dir_name = f"{name}_{self._model}_{Path(image_path).name}" # example: exp_result_gpt-4o_book
        save_dir = increment_path(path=Path(save_path)/dir_name)  # increment run
        
        return image_loader, prompt, save_dir

    def _process_images(self, image_loader: ImageLoader, prompt: str, save_result: bool, save_dir: Path, save_format: str) -> dict:
        response_dict = {}
        for image_file_path in image_loader:
            encoded_image = self.image_processor.process_image(image_file_path)
            response = self._generate_response(encoded_image, prompt)
            response_dict = self._handle_response(response, image_file_path)
            self._save_response(response_dict, image_file_path, save_result, save_dir, save_format)
        return response_dict
    
    def _handle_response(self, response, image_file_path) -> dict:
        return self.response_handler.handle_response(response, image_file_path)
    
    def _save_response(self, response_dict, image_file_path, save_result, save_dir, save_format) -> None:
        save_file_path = save_dir / "preds" / Path(image_file_path).parents[1].name
        self.response_handler.save_response(response_dict, save_file_path, Path(image_file_path).stem, save_result, save_format)
    
    @abstractmethod
    def _generate_response(self, encoded_image, prompt) -> any:
        pass

class ChatGPTModel(Model):
    def __init__(self, api_key: str, model_name: str, image_processor: ImageProcessor, response_handler: ResponseHandler, model_config: dict) -> None:
        super().__init__(api_key, model_name, image_processor, response_handler, model_config)
        self._client = None

    def _generate_response(self, encoded_image, prompt) -> any:
        return self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"},
            **self._kwargs  
        )

    def run(self, prompt_path: str, image_path: str, 
            save_result: bool = True, 
            save_path: str = f"{ROOT}/runs/", 
            save_format: str = "json", # "json" or "txt"
            name: str = f"exp_result") -> dict:
        try:
            if self._client is None:
                self._client = OpenAI(api_key=self._api_key)

            image_loader, prompt, save_dir = self._initialize_run(prompt_path, image_path, name, save_path)
            response_dict = self._process_images(image_loader, prompt, save_result, save_dir, save_format)

            if save_result:
                print(f"Results saved to {save_dir}")

            return response_dict
        
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing error: {e}")  # Handle JSON parsing error
        except Exception as e:
            raise Exception(f"Error occurred: {e}")

class GeminiModel(Model):
    def __init__(self, api_key: str, model_name: str, image_processor: ImageProcessor, response_handler: ResponseHandler, model_config: dict) -> None:
        super().__init__(api_key, model_name, image_processor, response_handler, model_config)
        self._gemini = None

    def _generate_response(self, encoded_image, prompt) -> any:
        return self._gemini.generate_content(
            [encoded_image, prompt],
            generation_config=GenerationConfig(response_mime_type="application/json", **self._kwargs),
        )

    def run(self, prompt_path: str, image_path: str, 
            save_result: bool = True, 
            save_path: str = f"{ROOT}/runs/", 
            save_format: str = "json", # "json" or "txt"
            name: str = f"exp_result") -> dict:
        try:
            if self._gemini is None:
                genai.configure(api_key=self._api_key)
                self._gemini = genai.GenerativeModel(model_name=self._model)

            image_loader, prompt, save_dir = self._initialize_run(prompt_path, image_path, name, save_path)
            response_dict = self._process_images(image_loader, prompt, save_result, save_dir, save_format)

            if save_result:
                print(f"Results saved to {save_dir}")

            return response_dict
        
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing error: {e}")  # Handle JSON parsing error
        except Exception as e:
            raise Exception(f"Error occurred: {e}")  # Handle other exceptions with more specific message

"""
Helper functions
"""

def load_model(model_name: str, model_config_path: str = None, **kwargs) -> ChatGPTModel | GeminiModel:
    """Load a model from the model registry.

    Args:
        model_name: Name of the model to load (e.g., 'openai::gpt-4o-mini')
        **kwargs: Additional arguments to pass to the model constructor
            temperature: float = Controls randomness in the output
            top_p: float = Controls diversity via nucleus sampling
            top_k: int = Controls diversity via top-k sampling
            max_tokens: int = Maximum number of tokens to generate
            repeat_penalty: float = Penalty for repeating tokens

    Examples:
    >>> model = load_model('openai::gpt-4o-mini', temperature=0.8)
    >>> model = load_model('google::gemini-1.5-pro', top_k=10, top_p=0.9)
    >>> model = load_model('openai::gpt-4o-mini', model_config_path='./config/openai/gpt-4o-mini.json(txt, yaml, csv)')
    """
    load_dotenv()
    model_config = {}

    if model_config_path is not None:
        model_config_loader = ModelConfigLoader(model_config_path)
        model_config = model_config_loader.get_config()
    
    model_config.update(**kwargs)

    if "openai::" in model_name:
        model_name = model_name.split("::")[1]
        return ChatGPTModel(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=model_name,
            image_processor=ChatGPTImageProcessor(),
            response_handler=ChatGPTResponseHandler(),
            model_config=model_config
        )

    if "google::" in model_name:
        model_name = model_name.split("::")[1]
        return GeminiModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=model_name,
            image_processor=GeminiImageProcessor(),
            response_handler=GeminiResponseHandler(),
            model_config=model_config
        )
    else:
        raise ValueError(f"Model {model_name} not found.")