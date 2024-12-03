import argparse

from logos_pipe_ocr.core.model import load_model

def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--image-path", type=str, required=True, help="Image path(directory or file)")
    parser.add_argument("--prompt-file-path", type=str, required=True, help="Prompt file path")
    parser.add_argument("--model-name", type=str, required=True, help="Model name")
    parser.add_argument("--model-config-path", type=str, required=False, help="Model config file path(optional)", default=None)

def main(image_path: str, prompt_file_path: str, model_name: str, model_config_path: str):
    # load the model and run the model
    model = load_model(model_name, model_config_path)
    model.run(prompt_file_path, image_path) # TODO: Need to move prompt_file_path to the load_model function?

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="logos-pipe-ocr: Document Parsing CLI")
    add_arguments(parser)
    args = parser.parse_args()
    main(args.image_path, args.prompt_file_path, args.model_name, args.model_config_path)

