"""
This module contains the Image class for the Logos-pipe-ocr project.
"""

import os
IMAGE_EXTENSION = ".png"

class Image:
    def __init__(self, image_path: str):
        self._image_path = image_path
        self._image_file_paths = []

    def check_image_file_path(self):
        if not os.path.exists(self._image_path):  # Check if the file exists
            print(f"File not found, please check the file path. {self._image_path}")
            return []
        
        # get the image file path
        try:
            for root, dirs, files in os.walk(self._image_path):
                for file in files:
                    if file.endswith(IMAGE_EXTENSION):
                        self._image_file_paths.append(os.path.join(root, file))
        except Exception as e:
            print(f"An error occurred while accessing the directory: {e}")
            return []

        if len(self._image_file_paths) == 0:
            print(f"Image file not found, please check the directory. {self._image_path}")
            return []
        
        return self._image_file_paths
    
    def get_image_file_path(self):
        return self._image_file_paths[0]

    def get_image_file_paths(self):
        return self._image_file_paths
