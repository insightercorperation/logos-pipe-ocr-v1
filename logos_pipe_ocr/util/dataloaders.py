"""
This module contains the Image class for the Logos-pipe-ocr project.
"""

import os
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
LABEL_EXTENSIONS = [".json", ".txt"]
ENCODING_FORMAT = "utf-8-sig"

class ImageLoader:
    def __init__(self, image_path: str):
        """
        Initialize the ImageLoader with the path to the images.

        :param image_path: Path to the directory containing images.
        """
        self._image_path = image_path
        self._image_file_paths = []
        self._current_index = 0
        
        if not os.path.exists(self._image_path):
            raise FileNotFoundError(f"File not found, please check the file path. {self._image_path}")
        
        for root, _, files in os.walk(self._image_path):
            self._image_file_paths.extend(os.path.join(root, f) for f in files if any(f.endswith(suffix) for suffix in IMAGE_EXTENSIONS))
        
        if not self._image_file_paths:
            raise FileNotFoundError("No images found in the specified directory.")

    def __str__(self) -> str:
        """Return a string representation of the loaded images."""
        return f"Loaded images: {self._image_file_paths}"
    
    def __len__(self) -> int:
        """Return the number of loaded images."""
        return len(self._image_file_paths)
    
    def __iter__(self):
        """Return the iterator object."""
        return self

    def __next__(self) -> str:
        """Return the next image file path."""
        if self._current_index >= len(self._image_file_paths):
            raise StopIteration
        
        image_path = self._image_file_paths[self._current_index]
        self._current_index += 1
        return image_path

    def get_file_path(self) -> list[str]:
        """Return the list of image file paths."""
        return self._image_file_paths


"""
This module contains the Prompt class for the Logos-pipe-ocr project.
"""

class PromptLoader:
    def __init__(self, prompt_path: str):
        """
        Initialize the PromptLoader with the path to the prompt file.

        :param prompt_path: Path to the prompt file.
        """
        self._prompt_path = prompt_path
        self._prompt = None

        if not os.path.exists(self._prompt_path):
            raise FileNotFoundError(f"File not found, please check the file path. {self._prompt_path}")
        
        with open(self._prompt_path, 'r', encoding=ENCODING_FORMAT) as file:
            self._prompt = file.read()
        
    def __str__(self) -> str:
        """Return a string representation of the prompt."""
        return f"Prompt: {self._prompt}"

    def __len__(self) -> int:
        """Return the length of the prompt."""
        return len(self._prompt)
        
    def get_prompt(self) -> str:
        """Return the loaded prompt."""
        return self._prompt
    
    def update_prompt(self, prompt: str) -> None:
        """
        Update the prompt in the file.

        :param prompt: New prompt text to write to the file.
        """
        try:
            with open(self._prompt_path, 'w', encoding=ENCODING_FORMAT) as file:
                file.write(prompt)
        except Exception as e:
            raise Exception(f"Error occurred: {e}")
        
"""
This module contains the EvalDataLoader class for the Logos-pipe-ocr project.
"""
class EvalDataLoader:
    def __init__(self, label_dir_path: str, output_dir_path: str):
        """
        Initialize the EvalDataLoader with the path to the label files and output files.

        :param label_dir_path: Path to the label directory.
        :param output_dir_path: Path to the output directory.
        """
        self._label_dir_path = label_dir_path
        self._output_dir_path = output_dir_path
        self._label_file_paths = []
        self._output_file_paths = []
        self._current_index = 0 

        if not os.path.exists(self._label_dir_path) or not os.path.exists(self._output_dir_path):
            raise FileNotFoundError(f"Directory not found, please check the file path. {self._label_dir_path} or {self._output_dir_path}")

        for root, _, files in os.walk(self._label_dir_path):
            self._label_file_paths.extend(os.path.join(root, f) for f in files if any(f.endswith(suffix) for suffix in LABEL_EXTENSIONS))
        
        for root, _, files in os.walk(self._output_dir_path):
            for f in files:
                output_path = os.path.join(root, f)
                if os.path.basename(output_path) in [os.path.basename(lp) for lp in self._label_file_paths]:
                    self._output_file_paths.append(output_path)
                else:
                    print(f"Warning: No corresponding label file for {f}")

        # get only the files that have corresponding label files
        self._label_file_paths = [label_path for label_path in self._label_file_paths if os.path.basename(label_path) in [os.path.basename(op) for op in self._output_file_paths]]
        self._output_file_paths = [output_path for output_path in self._output_file_paths if os.path.basename(output_path) in [os.path.basename(lp) for lp in self._label_file_paths]]

    def __len__(self) -> int:
        """Return the number of label and output file paths."""
        return len(self._label_file_paths)

    def __iter__(self):
        """Return the iterator object."""
        return self

    def __next__(self) -> tuple[str, str]:
        """Return the next label and output file paths."""
        if self._current_index >= len(self._label_file_paths):
            raise StopIteration
        
        label_path = self._label_file_paths[self._current_index]
        output_path = self._output_file_paths[self._current_index]
        self._current_index += 1
        return label_path, output_path

    def get_label_file_paths(self) -> list[str]:
        """Return the list of label file paths."""
        return self._label_file_paths

    def get_output_file_paths(self) -> list[str]:
        """Return the list of output file paths."""
        return self._output_file_paths