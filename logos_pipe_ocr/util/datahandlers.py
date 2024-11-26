"""
This module contains the data handler classes for the Logos-pipe-ocr project.
"""

from abc import ABC, abstractmethod
import base64
import json
import PIL.Image

class ImageProcessor(ABC):
    @abstractmethod
    def process_image(self, image_file_path: str) -> str:
        pass

class ChatGPTImageProcessor(ImageProcessor):
    def process_image(self, image_file_path: str) -> str:
        try:
            with open(image_file_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Image processing error: {e}")

class GeminiImageProcessor(ImageProcessor):
    def process_image(self, image_file_path: str) -> bytes:
        try:
            with PIL.Image.open(image_file_path) as img:
                return img
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
        file_name = image_file_path.split("/")[-1]
        if isinstance(response_dict, list):
            for item in response_dict:
                item["file_name"] = file_name
        else:
            response_dict["file_name"] = file_name

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
            response_dict = response_json.get("questions", response_json)
            self.add_file_name(response_dict, image_file_path)
            return response_dict
        return {}

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
            response_dict = response_json.get("questions", response_json)
            self.add_file_name(response_dict, image_file_path)
            return response_dict
        return {}