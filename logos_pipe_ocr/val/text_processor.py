import re
from abc import ABC, abstractmethod

class Preprocess(ABC):
    @abstractmethod
    def run(self, input_data: dict | list[dict], input_data2: dict | list[dict] = None) -> tuple[dict | list[dict]]:
        pass

class TextProcessor(Preprocess):
    """ Process the input data by converting it to a string, removing special characters, and normalizing the string.

    Args:
        input_data (dict | list[dict]): The input data to be processed.
        input_data2 (dict | list[dict], optional): The second input data to be processed. Defaults to None.
    
    Returns:
        tuple[dict | list[dict]]: The processed data.
    """
    def __init__(self):
        pass

    def run(self, input_data: dict | list[dict], input_data2: dict | list[dict] = None) -> tuple[dict | list[dict]]:
        return self.preprocess(input_data), self.preprocess(input_data2)

    def preprocess(self, input_data: dict | list[dict]) -> tuple[dict | list[dict]]:  # 메서드 이름 변경
        if input_data is None:
            return None
        elif isinstance(input_data, list):
            return [self._text_processing_single_dict(data) for data in input_data]
        else:
            return self._text_processing_single_dict(input_data)

    def _text_processing_single_dict(self, input_dict: dict) -> dict:  # 메서드 이름 변경
        processed_dict = {}
        for key, value in input_dict.items():
            if key == "file_name":
                processed_dict[key] = value
            else:
                if isinstance(value, list):
                    processed_dict[key] = [self._process_string(item) for item in value]  # 메서드 호출 변경
                else:
                    processed_dict[key] = self._process_string(value)  # 메서드 호출 변경
        
        return processed_dict

    def _process_string(self, value: str) -> str:  # 메서드 이름 변경
        if value == "" or value is None:
            return None
        elif isinstance(value, bool):
            return value
        else:
            cleaned_string = convert_to_string(value)
            cleaned_string = convert_choice(cleaned_string)
            cleaned_string = remove_special_characters_with_equation(cleaned_string)
            cleaned_string = remove_all_whitespace(cleaned_string)
            cleaned_string = remove_extra_spaces(cleaned_string)
            return normalize_string(cleaned_string)  # 최종 문자열 반환


def convert_to_string(input_string: str) -> str:  # Convert input to string
    if isinstance(input_string, (int, float)):
        return str(input_string)
    else:
        return input_string
    
def convert_choice(input_string: str) -> str: # Convert choices
    choice_mapping = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5"}
    pattern = re.compile('|'.join(re.escape(key) for key in choice_mapping.keys()))
    return pattern.sub(lambda match: choice_mapping[match.group(0)], input_string)

def remove_extra_spaces(input_string: str) -> str:  # Remove unnecessary spaces
    return ' '.join(input_string.split()).strip()  # Split the string by spaces, then join them back with a single space, and remove extra spaces on both sides

def remove_all_whitespace(input_string: str) -> str:  # Remove all unnecessary tabs and newlines
    return re.sub(r'[\t\n]+', '', input_string)

def remove_special_characters_with_equation(input_string: str) -> str: # Remove special characters
    # Find the equation part and keep it unchanged
    def replace_equation(match):
        return match.group(0)  # Keep the equation part unchanged

    # Remove special characters from the rest of the string
    cleaned_string = re.sub(r'(\$.*?\$|\(.*?\)|\{.*?\}|[a-zA-Z0-9^ +\-*/=(){}<>]+)', replace_equation, input_string)  # Keep the equation part
    cleaned_string = re.sub(r'[^a-zA-Z가-힣ㄱ-ㅎ0-9\s+*/=^(){}<>#?!.]', '', cleaned_string)  # Remove all characters except alphabets, numbers, spaces, Korean (including consonants), mathematical symbols, and '#'
    cleaned_string = ' '.join(cleaned_string.split())  # Remove unnecessary spaces
    return cleaned_string

def normalize_string(input_string: str) -> str:  # Convert string to lowercase
    return input_string.lower()  # Convert to lowercase
