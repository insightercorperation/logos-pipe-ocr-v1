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
from logos_pipe_ocr.util.file import increment_path, read_json_file
from logos_pipe_ocr.util.datahandlers import *
from logos_pipe_ocr.util.dataloaders import ImageLoader, PromptLoader

FILE_DIR = Path(__file__).resolve()
ROOT = FILE_DIR.parents[1]

class Model(ABC):  # Abstract Base Class for all models
    def __init__(self):
        self._model = None
        self._api_key = None
        self.response_handler = None
        self.image_processor = None
        self._kwargs = None
        
    @abstractmethod
    def run(self, prompt_path: str, image_paths: str, 
            save_result: bool, # save result
            save_path: str, # save path
            save_format: str, # "json" or "txt"
            name: str) -> dict: # result name 
        pass

class ChatGPTModel(Model):
    def __init__(self, api_key: str, model_name: str, image_processor: ImageProcessor, response_handler: ResponseHandler, **kwargs):
        super().__init__()
        self._api_key = api_key
        self._model = model_name
        self.image_processor = image_processor
        self.response_handler = response_handler
        self._kwargs = kwargs
        self._client = None

    def run(self, prompt_path: str, image_path: str, 
            save_result: bool = True, 
            save_path: str = f"{ROOT}/runs/", 
            save_format: str = "txt", # "json" or "txt"
            name: str = f"exp_result") -> dict:
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key)

        image_loader = ImageLoader(image_path)
        prompt = PromptLoader(prompt_path).get_prompt()
        response_dict = {}

        # Save directory
        dir_name = f"{name}_{self._model}_{Path(image_path).name}" # example: exp_result_gpt-4o_book
        save_dir = increment_path(path=Path(save_path)/dir_name)  # increment run
        try:
            for image_file_path in image_loader:
                encoded_image = self.image_processor.process_image(image_file_path)
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                        ]
                    }],
                    response_format={"type": "json_object"},
                    **self._kwargs  
                )
                # Save the response to the save directory (Only if save_result is True)
                save_file_path = save_dir / "preds" / Path(image_file_path).parents[1].name if save_result else None
                response_dict = self.response_handler.handle_response(response, image_file_path)
                self.response_handler.save_response(response_dict, save_file_path, Path(image_file_path).stem, save_result, save_format)

            if save_result:
                print(f"Results saved to {save_dir}")

        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing error: {e}")  # Handle JSON parsing error
        except Exception as e:
            raise Exception(f"Error occurred: {e}")  # Handle other exceptions with more specific message

class GeminiModel(Model):
    def __init__(self, api_key: str, model_name: str, image_processor: ImageProcessor, response_handler: ResponseHandler, **kwargs):
        super().__init__()
        self._api_key = api_key
        self._model = model_name
        self.image_processor = image_processor
        self.response_handler = response_handler
        self._kwargs = kwargs
        self._gemini = None

    def run(self, prompt_path: str, image_path: str, 
            save_result: bool = True, 
            save_path: str = f"{ROOT}/runs/", 
            save_format: str = "txt", # "json" or "txt"
            name: str = f"exp_result") -> dict:
        try:
            if self._gemini is None:
                genai.configure(api_key=self._api_key)
                self._gemini = genai.GenerativeModel(model_name=self._model)

            image_loader = ImageLoader(image_path)
            prompt = PromptLoader(prompt_path).get_prompt()
            response_dict = {}

            # Save directory
            dir_name = f"{name}_{self._model}_{Path(image_path).name}" # example: exp_result_gpt-4o_book
            save_dir = increment_path(path=Path(save_path)/dir_name)  # increment run

            for image_file_path in image_loader:
                image_data = self.image_processor.process_image(image_file_path)
                response = self._gemini.generate_content(
                    [image_data, prompt],
                    generation_config=GenerationConfig(response_mime_type="application/json", **self._kwargs),
                )
                # Save the response to the save directory (Only if save_result is True)
                save_file_path = save_dir / "preds" / Path(image_file_path).parents[1].name if save_result else None
                print(response.text)
                response_dict = self.response_handler.handle_response(response, image_file_path)
                self.response_handler.save_response(response_dict, save_file_path, Path(image_file_path).stem, save_result, save_format)
            
            if save_result:
                print(f"Results saved to {save_dir}")
        
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
    >>> model = load_model('openai::gpt-4o-mini', model_config_path='./config/openai/gpt-4o-mini.json')
    """
    load_dotenv()
    if model_config_path is not None: # load model config
        model_config = read_json_file(model_config_path)
        kwargs.update(model_config)

    if "openai::" in model_name:
        model_name = model_name.split("::")[1]
        return ChatGPTModel(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=model_name,
            image_processor=ChatGPTImageProcessor(),
            response_handler=ChatGPTResponseHandler(),
            **kwargs
        )

    if "google::" in model_name:
        model_name = model_name.split("::")[1]
        return GeminiModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=model_name,
            image_processor=GeminiImageProcessor(),
            response_handler=GeminiResponseHandler(),
            **kwargs
        )
    else:
        raise ValueError(f"Model {model_name} not found.")