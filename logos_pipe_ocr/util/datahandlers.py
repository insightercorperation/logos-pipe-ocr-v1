"""
This module contains the data handler classes for the Logos-pipe-ocr project.
"""
import os
import base64
import json
from PIL import Image
from io import BytesIO
from abc import ABC, abstractmethod
from logos_pipe_ocr.util.dataloaders import EvalDataLoader
from logos_pipe_ocr.util.file import read_json_file, read_txt_file, save

class ImageProcessor(ABC):
    @abstractmethod
    def process_image(self, image_file_path: str) -> bytes:
        pass

class ChatGPTImageProcessor(ImageProcessor):
    def process_image(self, image_file_path: str) -> bytes:
        try:
            with open(image_file_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Image processing error: {e}")

class GeminiImageProcessor(ImageProcessor):
    def process_image(self, image_file_path: str) -> bytes:
        try:
            with Image.open(image_file_path) as img:
                img_byte_arr = BytesIO()
                return img_byte_arr.getvalue()
        except Exception as e:
            raise Exception(f"Image processing error: {e}")
    
class ResponseHandler(ABC):
    @abstractmethod
    def handle_response(self, response: any, image_file_path: str) -> dict:
        """Handle the response from the image processing service.

        Args:
            response (any): The response object from the service.
            image_file_path (str): The path to the image file.

        Returns:
            dict: A dictionary containing the processed response.
        """
        pass

    def add_file_name(self, response_dict, image_file_path: str): # Add file name to response dictionary due to permission issue
        file_name = os.path.basename(image_file_path)
        if isinstance(response_dict, list):
            for item in response_dict:
                item["file_name"] = file_name
        else:
            response_dict["file_name"] = file_name
    
    def save(self, response_dict, save_file_path: str, file_name: str, save_result: bool, save_format: str):
        save(response_dict, save_file_path, file_name, save_result, save_format)


class ChatGPTResponseHandler(ResponseHandler):
    def handle_response(self, response: any, image_file_path: str) -> dict:
        """Handle the response from ChatGPT.

        Args:
            response (any): The response object from ChatGPT.
            image_file_path (str): The path to the image file.

        Returns:
            dict: A dictionary containing the processed response.
        """
        if response.choices[0].message.content is not None:
            response_json = json.loads(response.choices[0].message.content)
            self.add_file_name(response_json, image_file_path)
            return response_json
        return {}
    
    def save_response(self, response_dict, save_file_path: str, file_name: str, save_result: bool, save_format: str):
        self.save(response_dict, save_file_path, file_name, save_result, save_format)

class GeminiResponseHandler(ResponseHandler):
    def handle_response(self, response: any, image_file_path: str) -> dict:
        """Handle the response from Gemini.

        Args:
            response (any): The response object from Gemini.
            image_file_path (str): The path to the image file.

        Returns:
            dict: A dictionary containing the processed response.
        """
        if response.candidates:
            response_json = json.loads(response.text)
            self.add_file_name(response_json, image_file_path)
            return response_json
        return {}
    
    def save_response(self, response_dict, save_file_path: str, file_name: str, save_result: bool, save_format: str):
        self.save(response_dict, save_file_path, file_name, save_result, save_format)


class EvalDataHandler(EvalDataLoader):
    """ Handle the evaluation data by inheriting from EvalDataLoader.

    Args:
        label_dir_path (str): The path to the label directory.
        output_dir_path (str): The path to the output directory.
    
    Returns:
        eval_data (dict): A dictionary containing the processed data.  
    """
    def __init__(self, label_dir_path: str, output_dir_path: str):
        super().__init__(label_dir_path, output_dir_path)

    def __call__(self) -> dict:
        label_file_paths = self.get_label_file_paths()
        output_file_paths = self.get_output_file_paths()
        self._current_index = 0
        
        processed_data = []
        self.eval_data = {}

        for label, output in zip(label_file_paths, output_file_paths):
            if label.endswith(".json") and output.endswith(".json"):
                processed_item = {
                    "label": read_json_file(label),
                    "output": read_json_file(output),
                }
            elif label.endswith(".txt") and output.endswith(".txt"):
                processed_item = {
                    "label": read_txt_file(label),
                    "output": read_txt_file(output),
                }
            else:
                raise ValueError(f"Unsupported file extension: {label} or {output}")
            
            processed_data.append(processed_item)

        self.eval_data["processed_data"] = processed_data
        return self.eval_data
    
    def __len__(self) -> int:
        return len(self.eval_data["processed_data"])
    
    def __getitem__(self, index: int) -> dict:
        return self.eval_data["processed_data"][index]
    
    def __iter__(self):
        for item in self.eval_data.get("processed_data", []):
            yield item["label"], item["output"]
    
    def __next__(self):
        if self._current_index >= len(self.eval_data["processed_data"]):
            raise StopIteration
        item = self.eval_data["processed_data"][self._current_index]
        self._current_index += 1
        return item

    def get_eval_data(self) -> dict:
        return self.eval_data

    def get_label_data(self):
        return [item["label"] for item in self.eval_data["processed_data"]]

    def get_output_data(self):
        return [item["output"] for item in self.eval_data["processed_data"]]