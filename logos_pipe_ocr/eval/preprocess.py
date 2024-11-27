import re

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
    cleaned_string = re.sub(r'[^a-zA-Z가-힣ㄱ-ㅎ0-9\s+*/=^(){}<>#]', '', cleaned_string)  # Remove all characters except alphabets, numbers, spaces, Korean (including consonants), mathematical symbols, and '#'
    cleaned_string = ' '.join(cleaned_string.split())  # Remove unnecessary spaces
    return cleaned_string

def normalize_string(input_string: str) -> str:  # Convert string to lowercase
    return input_string.lower()  # Convert to lowercase

def text_processing(input_data: dict | list[dict]) -> dict | list[dict]:  # Change input to dict
    if isinstance(input_data, list):
        return [_text_processing_single_dict(data) for data in input_data]
    else:
        return _text_processing_single_dict(input_data)

def _text_processing_single_dict(input_dict: dict) -> dict: # Process single dict
    processed_dict = {}
    for key, value in input_dict.items():
        if key == "file_name":
            processed_dict[key] = value
        else:
            if isinstance(value, list):
                processed_dict[key] = [_process_string(item) for item in value]  # Use string processing function
            else:
                processed_dict[key] = _process_string(value)  # Use string processing function
    
    return processed_dict

def _process_string(value: str) -> str:  # String processing function
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
        return normalize_string(cleaned_string)  # Return the final string
