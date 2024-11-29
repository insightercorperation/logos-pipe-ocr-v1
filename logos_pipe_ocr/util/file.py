import json
import os
from pathlib import Path

ENCODING_FORMAT = 'utf-8-sig'

def create_txt_file(text: str|dict, file_path: str, file_name: str) -> None: # Function to save a text file
    try:
        if isinstance(text, list):  
            text = "\n".join(str(item) for item in text)  
        else:
            text = str(text)
        with open(str(file_path) + '/' + file_name + '.txt', 'w', encoding=ENCODING_FORMAT) as file:
            file.write(text)    
    except Exception as e:
        raise Exception(f"An error occurred while creating a TXT file: {str(e)}")   

def create_json_file(data: dict, file_path: str, file_name: str) -> None: # Function to save a JSON file
    try:
        with open(str(file_path) + '/' + file_name + '.json', 'w', encoding=ENCODING_FORMAT) as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise Exception(f"An error occurred while creating a JSON file: {str(e)}")

def read_json_file(file_path: str) -> dict: # Function to read a JSON file
    if not os.path.exists(file_path):
        print(f"File not found, please check the file path. {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding=ENCODING_FORMAT) as file:
            return json.load(file)
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def read_txt_file(file_path: str) -> list | str: # Function to read a TXT file and return a list or a single string
    if not os.path.exists(file_path):
        print(f"File not found, please check the file path. {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding=ENCODING_FORMAT) as file:
            content = file.read()
            lines = content.splitlines() 
            return lines if len(lines) > 1 else lines[0]  
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def increment_path(path, exist_ok=False, sep="", mkdir=False): # Function to increment a file or directory path if it exists
    """
    Generates an incremented file or directory path if it exists, with optional mkdir; args: path, exist_ok=False,
    sep="_", mkdir=False.

    Example: runs/exp --> runs/exp{sep}1, runs/exp{sep}2, ... etc 
    """ 
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(""), path.suffix) if path.is_file() else (path, "")

        for n in range(2, 9999):
            p = f"{path}{sep}{n}{suffix}"  # increment path
            if not os.path.exists(p):  #
                break
        path = Path(p)

    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory

    return path

def save(data: any, save_file_path: str, file_name: str, save_result: bool = True, save_format: str = "json"):
    if save_result:  # save_result가 True일 때만 저장
        (save_file_path).mkdir(parents=True, exist_ok=True)
        if str(save_format).lower() == "json":   
            create_json_file(data, file_path=save_file_path, file_name=file_name)  # 결과 저장
        elif str(save_format).lower() == "txt":
            create_txt_file(data, file_path=save_file_path, file_name=file_name)  # 결과 저장
    
        