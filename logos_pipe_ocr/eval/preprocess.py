import re

def convert_choice(input_string: str) -> str: # 선택지 변환
    choice_mapping = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5"}
    pattern = re.compile('|'.join(re.escape(key) for key in choice_mapping.keys()))
    return pattern.sub(lambda match: choice_mapping[match.group(0)], input_string)

def remove_extra_spaces(input_string: str) -> str:  # 불필요한 공백을 제거하는 함수
    return ' '.join(input_string.split()).strip()  # 문자열을 공백으로 나누고, 다시 하나의 공백으로 연결 후 양쪽 공백 제거

def remove_all_whitespace(input_string: str) -> str:  # 모든 불필요한 탭과 줄바꿈 문자를 제거하는 함수
    return re.sub(r'[\t\n]+', '', input_string)

def remove_special_characters_with_equation(input_string: str) -> str: # 특수 문자 제거
    # 수식 부분을 찾고, 그 외의 부분에서 특수 문자를 제거
    def replace_equation(match):
        return match.group(0)  # 수식 부분은 그대로 유지

    # 수식 부분을 제외한 나머지에서 특수 문자 제거
    cleaned_string = re.sub(r'(\$.*?\$|\(.*?\)|\{.*?\}|[a-zA-Z0-9^ +\-*/=(){}]+)', replace_equation, input_string)  # 수식 부분 유지
    cleaned_string = re.sub(r'[^a-zA-Z가-힣ㄱ-ㅎ0-9\s+*/=^(){}#]', '', cleaned_string)  # 알파벳, 숫자, 공백, 한국어(자음 포함), 수식 기호, '#'을 제외한 모든 문자 제거
    cleaned_string = ' '.join(cleaned_string.split())  # 불필요한 공백 제거
    return cleaned_string

def normalize_string(input_string: str) -> str:  # 영문자열을 소문자로 변환하는 함수
    return input_string.lower()  # 소문자로 변환

def text_processing(input_data: dict | list[dict]) -> dict | list[dict]:  # 입력을 dict로 변경
    if isinstance(input_data, list):
        return [_text_processing_single_dict(data) for data in input_data]
    else:
        return _text_processing_single_dict(input_data)

def _text_processing_single_dict(input_dict: dict) -> dict: # 단일 dict 처리
    processed_dict = {}
    for key, value in input_dict.items():
        if value == "" or value is None:
            processed_dict[key] = None
        elif isinstance(value, bool):
            processed_dict[key] = value
        elif key == "file_name":
            processed_dict[key] = value
        else:
            if isinstance(value, list):
                processed_dict[key] = [_process_string(item) for item in value]  # 문자열 처리 함수 사용
            else:
                processed_dict[key] = _process_string(value)  # 문자열 처리 함수 사용
    
    return processed_dict

def _process_string(value: str) -> str:  # 문자열 처리 함수
    cleaned_string = convert_choice(value)
    cleaned_string = remove_special_characters_with_equation(cleaned_string)
    cleaned_string = remove_all_whitespace(cleaned_string)
    cleaned_string = remove_extra_spaces(cleaned_string)
    return normalize_string(cleaned_string)  # 최종 문자열 반환
