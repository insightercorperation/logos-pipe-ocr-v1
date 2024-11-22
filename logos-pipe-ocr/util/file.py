import json
import tempfile
import os
from pathlib import Path

def create_text_file(text: str, file_path: str) -> None: # 텍스트 파일을 저장하는 함수
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)    

def read_json_file(file_path: str) -> dict: # JSON 파일을 읽어오는 함수
    if not os.path.exists(file_path):
        print(f"File not found, please check the file path. {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def create_json_file(data: dict, file_path: str) -> None: # JSON 파일을 저장하는 함수
    try:
        with open(file_path + '.json', 'w', encoding='utf-8-sig') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise Exception(f"An error occurred while creating a JSON file: {str(e)}")
    
def increment_path(path, exist_ok=False, sep="", mkdir=False):
    """
    Generates an incremented file or directory path if it exists, with optional mkdir; args: path, exist_ok=False,
    sep="", mkdir=False.

    Example: runs/exp --> runs/exp_{sep}2, runs/exp_{sep}3, ... etc
    """
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(""), path.suffix) if path.is_file() else (path, "")

        # Method 1
        for n in range(2, 9999):
            p = f"{path}_{sep}{n}{suffix}"  # increment path
            if not os.path.exists(p):  #
                break
        path = Path(p)

    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory

    return path
    
        