"""
This module generates a JSON schema from a JSON file.
"""
from abc import ABC, abstractmethod

class SchemaGenerator(ABC):
    """Abstract class for generating JSON schemas."""
    @abstractmethod
    def generate_json_schema(self) -> dict:
        """Generate a JSON schema."""
        pass

    @abstractmethod
    def _process_data(self, schema: dict):
        """Process data into the schema."""
        pass

class JsonSchemaGenerator(SchemaGenerator):
    """generate json schema, required fields, boolean fields from json data"""
    def __init__(self, json_data: dict = None):
        self.json_data = json_data if json_data is not None else {}
        self.schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        self.required_fields = []
        self.boolean_fields = {}
        self.generate_json_schema()

    def generate_json_schema(self) -> dict:
        """Generate the JSON schema."""
        if self.json_data:
            self._process_data(self.schema)
            self.required_fields = self.get_required_fields()
            self.boolean_fields = self.get_boolean_fields()
        else:
            raise ValueError("JSON data is empty")

    def _process_data(self, schema: dict):
        """Process JSON data into the schema."""
        data_items = self.json_data[0] if isinstance(self.json_data, list) else self.json_data
        for key, value in data_items.items():
            schema["properties"][key] = self._get_type(value)
            schema["required"].append(key)

    def _get_type(self, value: dict | list | str | None) -> dict:
        """Return the type of the given value."""
        if isinstance(value, dict):
            return {"type": "object", "properties": JsonSchemaGenerator(value).get_properties()}
        elif isinstance(value, list):
            return {"type": "array", "items": self._get_type(value[0]) if value else self._get_type(None)}
        else:
            type_mapping = {
                int: "integer",
                float: "number",
                bool: "boolean",
                str: "string",
                type(None): "string" # if value is None, type is string
            }
            return {"type": type_mapping.get(type(value), "string")}
        
    def get_properties(self) -> dict:
        return self.schema["properties"]

    def get_required_fields(self) -> list:
        """Return the required fields."""
        return self.schema["required"]

    def get_boolean_fields(self) -> dict:
        """Return the boolean fields."""
        return {key: value for key, value in self.schema["properties"].items() if value["type"] == "boolean"}

    def get_schema(self) -> dict:
        """Return the schema."""
        return self.schema
