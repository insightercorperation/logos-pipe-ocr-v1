"""
This module contains the core model classes for the Logos-pipe-ocr project.
"""

import os
import json
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
import google.generativeai as genai
from google.generativeai import GenerationConfig
from abc import ABC, abstractmethod
from logos_pipe_ocr.util.file import create_json_file, increment_path, read_json_file
from logos_pipe_ocr.util.datahandlers import *
from logos_pipe_ocr.util.dataloaders import *

FILE_DIR = Path(__file__).resolve()
ROOT = FILE_DIR.parents[1]

class Model(ABC):  # Abstract Base Class for all models
    @abstractmethod
    def run(self, prompt_path: str, image_paths: str, 
            save_result: bool = True, # save result
            save_path: str = f"{ROOT}/output/", # save path
            name: str = f"exp_result") -> dict: # result name 
        pass

class ChatGPTModel(Model):
    def __init__(self, api_key: str, model_name: str, image_processor: ImageProcessor, response_handler: ResponseHandler, **kwargs):
        super().__init__()
        self._api_key = api_key
        self._model = model_name
        self._client = None
        self.image_processor = image_processor
        self.response_handler = response_handler
        self._kwargs = kwargs

    def run(self, prompt_path: str, image_path: str, 
            save_result: bool = True, 
            save_path: str = f"{ROOT}/output/", 
            name: str = f"exp_result") -> dict:
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key)

        image_file_paths = ImageLoader(image_path).get_file_path()
        prompt = PromptLoader(prompt_path).get_prompt()
        response_dict = {}

        # Save directory
        task_name = Path(image_path).name
        dir_name = f"{name}_{self._model}"
        save_dir = increment_path(path=Path(save_path)/dir_name, sep=task_name)  # increment run
        print(save_dir)
        try:
            for image_file_path in image_file_paths:
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
                
                response_dict = self.response_handler.handle_response(response, image_file_path)

                # Save the response to the save directory (Only if save_result is True)
                save_file_path = save_dir / "preds" / Path(image_file_path).parents[1].name
                (save_file_path).mkdir(parents=True, exist_ok=True) if save_result else None  # make dir
                create_json_file(response_dict, file_path=save_file_path, file_name=Path(image_file_path).name) if save_result else None # save result (if save_result is False, what should be done?)

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
        self._gemini = None
        self.image_processor = image_processor
        self.response_handler = response_handler
        self._kwargs = kwargs

    def run(self, prompt_path: str, image_path: str, 
            save_result: bool = True, 
            save_path: str = f"{ROOT}/output/", 
            name: str = f"exp_result") -> dict:
        try:
            if self._gemini is None:
                genai.configure(api_key=self._api_key)
                self._gemini = genai.GenerativeModel(model_name=self._model)

            image_file_paths = ImageLoader(image_path).get_file_path()
            prompt = PromptLoader(prompt_path).get_prompt()
            response_dict = {}

            # Save directory
            task_name = Path(image_path).name
            dir_name = f"{name}_{self._model}"
            save_dir = increment_path(path=Path(save_path)/dir_name, sep=task_name)  # increment run

            for image_file_path in image_file_paths:
                image_data = self.image_processor.process_image(image_file_path)
                response = self._gemini.generate_content(
                    [image_data, prompt],
                    generation_config=GenerationConfig(response_mime_type="application/json", **self._kwargs),
                )
                
                response_dict = self.response_handler.handle_response(response, image_file_path)

                # Save the response to the save directory (Only if save_result is True)
                save_file_path = save_dir / "preds" / Path(image_file_path).parents[1].name
                (save_file_path).mkdir(parents=True, exist_ok=True) if save_result else None  # make dir
                create_json_file(response_dict, file_path=save_file_path, file_name=Path(image_file_path).name) if save_result else None # save result (if save_result is False, what should be done?)
            
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