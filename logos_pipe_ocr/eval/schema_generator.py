"""
This module generates a JSON schema from a JSON file.
"""
from abc import ABC, abstractmethod

class generator(ABC):
    """Abstract class for generating JSON schemas."""
    @abstractmethod
    def generate_json_schema(self) -> dict:
        """Generate a JSON schema."""
        pass

    @abstractmethod
    def process_data(self, schema: dict):
        """Process data into the schema."""
        pass

class JsonSchemaGenerator(generator):
    """Generates a JSON schema from provided JSON data."""
    def __init__(self, json_data: dict):
        """Initialize with JSON data."""
        self.json_data = json_data

    def generate_json_schema(self) -> dict:
        """Generate the JSON schema."""
        schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        if self.json_data:
            self.process_data(schema)
        return schema

    def process_data(self, schema: dict):
        """Process JSON data into the schema."""
        if isinstance(self.json_data, list):
            for key, value in self.json_data[0].items():
                schema["properties"][key] = self.get_type(value)
                schema["required"].append(key)
        else:
            for key, value in self.json_data.items():
                schema["properties"][key] = self.get_type(value)
                schema["required"].append(key)

    def get_type(self, value: dict | list | str) -> dict:
        """Return the type of the given value."""
        if isinstance(value, dict):
            return {"type": "object", "properties": JsonSchemaGenerator(value).generate_json_schema()["properties"]}
        elif isinstance(value, list):
            return {"type": "array", "items": self.get_type(value[0]) if value else self.get_type(None)}
        else:
            # 모든 타입을 JSON 스키마에 맞는 문자열로 변환
            type_mapping = {
                int: "integer",
                float: "number",
                bool: "boolean",
                str: "string",
                type(None): "string" # if value is None, type is string
            }
            return {"type": type_mapping.get(type(value), "string")}
