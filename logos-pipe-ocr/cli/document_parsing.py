﻿import argparse

from logos_pipe_ocr.core.model import load_model
from logos_pipe_ocr.core.prompt import PromptLoader
from logos_pipe_ocr.core.image import Image

def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--image-path", type=str, required=True, help="Image path(directory or file)")
    parser.add_argument("--prompt-file-path", type=str, required=True, help="Prompt file path")
    parser.add_argument("--model-name", type=str, required=True, help="Model name")
    parser.add_argument("--model-config-path", type=str, required=False, help="Model config file path(optional)", default=None)

def main(image_path: str, prompt_file_path: str, model_name: str, model_config_path: str):
    # load the prompt and image
    prompt = PromptLoader(prompt_file_path).load_prompt()
    image_file_paths = Image(image_path).check_image_file_path()

    # load the model and run the model
    model = load_model(model_name, model_config_path)

    for image_file_path in image_file_paths:
        result = model.run(prompt, image_file_path)
        print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="logos-pipe-ocr: Document Parsing CLI")
    add_arguments(parser)
    args = parser.parse_args()
    main(args.image_path, args.prompt_file_path, args.model_name, args.model_config_path)
