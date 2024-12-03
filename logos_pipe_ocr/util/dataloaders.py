"""
This module contains the data loader classes for the Logos-pipe-ocr project.
"""

import os
from .file import read_yaml_file, read_json_file, create_txt_file

CONFIG_EXTENSIONS = [".yaml", ".json"]
IMAGE_EXTENSIONS = [".png", ".jpeg"]
LABEL_EXTENSIONS = [".json", ".txt"]
PROMPT_EXTENSIONS = ".txt"
ENCODING_FORMAT = "utf-8-sig"

class ImageLoader:
    """ ImageLoader class for loading images from a directory. 

    Args:
        image_path (str): Path to the directory containing images.

    Returns:
        image_file_paths (list[str]): List of image file paths.
    """
    def __init__(self, image_dir_path: str) -> None:
        self._image_dir_path = image_dir_path
        self._image_file_paths = []
        self._current_index = 0
        
        if not os.path.exists(self._image_dir_path):
            raise FileNotFoundError(f"Directory not found, please check the file path. {self._image_dir_path}")
        
        if os.path.getsize(self._image_dir_path) == 0:
            raise FileNotFoundError("The directory is empty. Please provide a valid image directory.")
        
        for root, _, files in os.walk(self._image_dir_path): # walk through the directory
            self._image_file_paths.extend(os.path.join(root, f) for f in files # get the file paths
                if any(f.endswith(suffix) for suffix in IMAGE_EXTENSIONS) and os.path.getsize(os.path.join(root, f)) > 0) # check if the file is an image and is not empty
            
        if not self._image_file_paths:
            raise FileNotFoundError("No images found in the specified directory.")


    def __str__(self) -> str:
        """Return a string representation of the loaded images."""
        return f"Loaded images: {self._image_file_paths}"
    
    def __len__(self) -> int:
        """Return the number of loaded images."""
        return len(self._image_file_paths)
    
    def __iter__(self) -> 'ImageLoader':
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
    def __init__(self, prompt_path: str) -> None:
        """ PromptLoader class for loading a prompt from a file.

        Args:
            prompt_path (str): Path to the prompt file.

        Returns:
            prompt (str): The loaded prompt.
        """
        self._prompt_path = prompt_path
        self._prompt = None

        if not os.path.exists(self._prompt_path):
            raise FileNotFoundError(f"File not found, please check the file path. {self._prompt_path}")
        if os.path.getsize(self._prompt_path) == 0:
            raise ValueError("The file is empty. Please provide a valid prompt file.")
        
        if self._prompt_path.endswith(PROMPT_EXTENSIONS): # differ with read_txt_file (read_txt_file is for the result file)
            with open(self._prompt_path, 'r', encoding=ENCODING_FORMAT) as file:
                self._prompt = file.read()
        else:
            raise ValueError(f"Unsupported file extension. Please use one of the following extensions: {', '.join(PROMPT_EXTENSIONS)}")
        
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
            create_txt_file(self._prompt_path, prompt)
        except Exception as e:
            raise Exception(f"Error occurred: {e}")
        
"""
This module contains the EvalDataLoader class for the Logos-pipe-ocr project.
"""
class EvalDataLoader:
    def __init__(self, label_dir_path: str, output_dir_path: str) -> None:
        """ EvalDataLoader class for loading label and output files from directories.

        Args:
            label_dir_path (str): Path to the label directory.
            output_dir_path (str): Path to the output directory.
        
        Returns:
            label_file_paths (list[str]): List of label file paths.
            output_file_paths (list[str]): List of output file paths.
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

    def __iter__(self) -> 'EvalDataLoader':
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
    
class ModelConfigLoader:
    """ ModelConfigLoader class for loading model configuration files.

    Args:
        config_file_path (str): Path to the model configuration file.

    Returns:
        config (dict): The loaded model configuration.
    """
    def __init__(self, config_file_path: str) -> None:
        self._config_file_path = config_file_path
        self._config = None

        if not os.path.exists(self._config_file_path):
            raise FileNotFoundError(f"Directory not found, please check the file path. {self._config_file_path}")
        
        if os.path.getsize(self._config_file_path) == 0:
            raise ValueError("The file is empty. Please provide a valid model configuration file.")
        
        self._data = self._load_file()
        self._load_parameters()

    def _load_file(self) -> dict:
        """Load configuration based on the file extension."""
        if self._config_file_path.endswith('.yaml'):
            return read_yaml_file(self._config_file_path)
        elif self._config_file_path.endswith('.json'):
            return read_json_file(self._config_file_path)
        else:
            raise ValueError(f"Unsupported file extension. Please use one of the following extensions: {', '.join(CONFIG_EXTENSIONS)}")
        
    def _load_parameters(self) -> dict:
        """Return the loaded configuration."""
        COMMON_ALLOWED_PARAMETERS = {
            "temperature",  # controls randomness in the output
            "top_p",  # cumulative probability-based sampling
            "top_k",  # top-k sampling
            "max_tokens",  # maximum number of tokens to generate
            "repeat_penalty",  # penalty for repeating tokens
            "seed",  # random seed
        }
        self._config = {key: self._data[key] for key in COMMON_ALLOWED_PARAMETERS if key in self._data}

    def get_config(self) -> dict:
        """Return the loaded configuration."""
        return self._config