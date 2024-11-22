"""
This module contains the core model classes for the Logos-pipe-ocr project.
"""

import os
import json
from openai import OpenAI
import base64
import PIL.Image
import google.generativeai as genai
from google.generativeai import GenerationConfig
from util.file_utils import create_json_file, increment_path
from abc import ABC, abstractmethod
from util.dataloaders import ImageLoader, PromptLoader
from dotenv import load_dotenv
from util.file import load_json_file, create_json_file

from pathlib import Path
import time

FILE_DIR = Path(__file__).resolve()
ROOT = FILE_DIR.parents[3]
OPERATION_TIME = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time() + 9 * 3600))

class Model(ABC):  # Abstract Base Class for all models
    @abstractmethod
    def run(self, prompt_path: str, image_paths: str, 
            save_result: bool = True, # save result
            save_path: str = f"{ROOT}/output/", # save path
            name: str = f"exp_result_{self._model}") -> dict: # result name 
        pass

class ChatGPTModel(Model): 
    def __init__(self, api_key: str, model_name: str, **kwargs):
        self._api_key = api_key
        self._model = model_name
        self._client = None # Initialize OpenAI client
        self._kwargs = kwargs
        
    def process_image(self, image_file_path: str) -> list[str]:
        try:
            encoded_image = None
            with open(image_file_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_image
        except Exception as e:
            raise Exception(f"Image processing error: {e}")

    def run(self, prompt_path: str, image_paths: str, 
            save_result: bool = True, # save result
            save_path: str = f"{ROOT}/output/", # save path
            name: str = f"exp_result_{self._model}") -> dict: # result name 
    
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key)

        image_file_paths = ImageLoader(image_paths).get_file_path()
        prompt = PromptLoader(prompt_path).get_prompt()
        response_dict = {}

        # Save directory
        save_dir = increment_path(Path(save_path) / name, exist_ok=True)  # increment run

        try:
            for image_file_path in image_file_paths:
                encoded_image = self.process_image(image_file_path)
                response = self._client.chat.completions.create(
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
                
                if response.choices[0].message.content is not None:
                    response_json = json.loads(response.choices[0].message.content)
                    response_dict = response_json.get("items", response_json)

                    if isinstance(response_dict, list):  # Check if it's a list
                        for item in response_dict: # Add file name manually due to permission issues
                            item["file_name"] = image_file_path.split("/")[-1] 
                    else:
                        response_dict["file_name"] = image_file_path.split("/")[-1]  
                
                    # Save the response to the save directory (Only if save_result is True)
                    (save_dir / "preds" / os.path.basename(os.path.dirname(image_file_path))).mkdir(parents=True, exist_ok=True) if save_result else None  # make dir
                    save_file_path = save_dir / "preds" / os.path.basename(os.path.dirname(image_file_path)) / os.path.basename(image_file_path)
                    create_json_file(response_dict, file_path=save_file_path) if save_result else None # save result (if save_result is False, what should be done?)

            if save_result:
                print(f"Results saved to {save_dir}")

        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing error: {e}")  # Handle JSON parsing error
        except Exception as e:
            raise Exception(f"Error occurred: {e}")  # Handle other exceptions with more specific message

class GeminiModel(Model): 
    def __init__(self, api_key: str, model_name: str, **kwargs):
        self._api_key = api_key
        self._model = model_name
        self._kwargs = kwargs
        self._gemini = None # Initialize Gemini client

    def process_image(self, image_path: str) -> bytes:  # Process single image
        try:
            with PIL.Image.open(image_path) as img:
                return img
        except Exception as e:
            raise Exception(f"Image processing error: {e}")

    def run(self, prompt_path: str, image_paths: str, 
            save_result: bool = True, # save result
            save_path: str = f"{ROOT}/output/", # save path
            name: str = f"exp_result_{self._model}") -> dict: # result name     
        try:
            if self._gemini is None:
                genai.configure(api_key=self._api_key)
                self._gemini = genai.GenerativeModel(model_name=self._model)

            image_file_paths = ImageLoader(image_paths).get_file_path()
            prompt = PromptLoader(prompt_path).get_prompt()
            response_dict = {}

            # Save directory
            save_dir = increment_path(Path(save_path) / name, exist_ok=True)  # increment run

            for image_file_path in image_file_paths:
                image_data = self.process_image(image_file_path)  # Process multiple images
                response = self._gemini.generate_content(
                    [image_data, prompt],
                    generation_config=GenerationConfig(response_mime_type="application/json", **self._kwargs),
                )
            
                if response.candidates:
                    response_json = json.loads(response.text)
                    if isinstance(response_json, list):
                        for item in response_json:
                            item["file_name"] = image_file_path.split("/")[-1]  # Add file name manually due to permission issues
                    else:
                        response_json["file_name"] = image_file_path.split("/")[-1]  # Add file name manually due to permission issues
                
                    # Save the response to the save directory (Only if save_result is True)
                    (save_dir / "preds" / os.path.basename(os.path.dirname(image_file_path))).mkdir(parents=True, exist_ok=True) if save_result else None  # make dir
                    save_file_path = save_dir / "preds" / os.path.basename(os.path.dirname(image_file_path)) / os.path.basename(image_file_path)
                    create_json_file(response_json, file_path=save_file_path) if save_result else None # save result (if save_result is False, what should be done?)
            
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
        model_config = load_json_file(model_config_path)
        kwargs.update(model_config)

    if "openai::" in model_name:
        model_name = model_name.split("::")[1]
        return ChatGPTModel(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=model_name,
            **kwargs
        )

    if "google::" in model_name:
        model_name = model_name.split("::")[1]
        return GeminiModel(
            api_key=os.getenv("GEMINI_API_KEY"),
            model_name=model_name,
            **kwargs
        )
    else:
        raise ValueError(f"Model {model_name} not found.")