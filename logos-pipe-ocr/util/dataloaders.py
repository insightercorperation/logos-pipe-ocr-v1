"""
This module contains the Image class for the Logos-pipe-ocr project.
"""

import os
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

class ImageLoader:
    def __init__(self, image_path: str):
        self._image_path = image_path
        self._image_file_paths = []
        self._current_index = 0
        
        if not os.path.exists(self._image_path):
            raise FileNotFoundError(f"File not found, please check the file path. {self._image_path}")
        
        for root, _, files in os.walk(self._image_path):
            self._image_file_paths.extend(os.path.join(root, f) for f in files if any(f.endswith(suffix) for suffix in IMAGE_EXTENSIONS))
        
        if not self._image_file_paths:
            raise FileNotFoundError("No images found in the specified directory.")

    def __str__(self):
        return f"Loaded images: {self._image_file_paths}"
    
    def __len__(self):
        return len(self._image_file_paths)

    def __next__(self):
        if self._current_index >= len(self._image_file_paths):
            raise StopIteration
        
        image_path = self._image_file_paths[self._current_index]
        self._current_index += 1
        return image_path

    def get_file_paths(self):
        return self._image_file_paths


"""
This module contains the Prompt class for the Logos-pipe-ocr project.
"""

class PromptLoader:
    def __init__(self, prompt_path: str):
        self._prompt_path = prompt_path
        self._prompt = None

        if not os.path.exists(self._prompt_path):
            raise FileNotFoundError(f"File not found, please check the file path. {self._prompt_path}")
        
        with open(self._prompt_path, 'r', encoding='utf-8') as file:
            self._prompt = file.read()
        
    def __str__(self):
        return f"Prompt: {self._prompt}"

    def __len__(self):
        return len(self._prompt)
        
    def get_prompt(self):
        return self._prompt
    
    def update_prompt(self, prompt: str):
        try:
            with open(self._prompt_path, 'w', encoding='utf-8') as file:
                file.write(prompt)
        except Exception as e:
            raise Exception(f"Error occurred: {e}")
    