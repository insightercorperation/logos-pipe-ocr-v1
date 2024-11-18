import json
import tempfile
import os

def read_prompt_file(prompt_file_path: str) -> str: # 저장된 prompt 파일을 읽어오는 함수
    with open(prompt_file_path, 'r', encoding='utf-8') as file:
        return file.read() 

def read_json_file(file_path: str) -> dict: # JSON 파일을 읽어오는 함수
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        return json.load(file)

def save_json_file(data: dict, file_path: str) -> None: # JSON 파일을 저장하는 함수
    try:
        with open(file_path + '.json', 'w', encoding='utf-8-sig') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"{file_path}.json 파일이 생성되었습니다.")
    except Exception as e:
        raise Exception(f"JSON 파일 저장 중 오류 발생: {str(e)}")

def create_temp_file(content: dict, filename: str = "temp") -> str: # 임시 파일을 생성하는 함수
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json', prefix=filename, dir='./temp/', mode='w', encoding='utf-8-sig') as temp_file:
            json.dump(content, temp_file, ensure_ascii=False, indent=4)
        print(f"임시 파일 {temp_file.name}이 생성되었습니다.")
        return temp_file.name # 임시 파일 경로 반환
    except Exception as e:
        raise Exception(f"임시 파일 생성 중 오류 발생: {str(e)}")

def delete_temp_file(file_path: str, delete_all = True) -> None:  # 임시 파일을 삭제하는 함수
    try:    
        if delete_all: # temp 디렉토리 내 모든 파일 삭제
            temp_dir = '../temp'
            for filename in os.listdir(temp_dir):
                file_to_delete = os.path.join(temp_dir, filename)
                os.remove(file_to_delete)
            print(f"임시 파일 {temp_dir} 내 모든 파일이 삭제되었습니다.")
        else:
            os.remove(file_path)
            print(f"임시 파일 {file_path}이 삭제되었습니다.")
    except Exception as e:
        raise Exception(f"임시 파일 삭제 중 오류 발생: {str(e)}")

    



    
        