"""
This module generates a JSON schema from a JSON file.
"""
from abc import ABC, abstractmethod

class SchemaGenerator(ABC):
    """Abstract class for generating JSON schemas."""
    @abstractmethod
    def generate_json_schema(self) -> None:
        """Generate a JSON schema."""
        pass

    @abstractmethod
    def _process_data(self) -> None:
        """Process data into the schema."""
        pass

class JsonSchemaGenerator(SchemaGenerator):
    """ Generate json schema, required fields, boolean fields from json data 

    Attributes:
        json_data (dict | list[dict]): The json data to generate the schema from.

    Returns:
        schema (dict): The generated JSON schema.
        required_fields (list): The required fields from the JSON schema.
        boolean_fields (dict): The boolean fields from the JSON schema.
    """
    def __init__(self, json_data: dict | list[dict]) -> None:
        self._json_data = json_data
        self.schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        self.required_fields = []
        self.boolean_fields = {}
        self.generate_json_schema()

    def generate_json_schema(self) -> None:
        """Generate the JSON schema."""
        if self._json_data:
            self._process_data() # process data into the schema
            self.required_fields = self._get_required_fields() # get required fields from processed schema
            self.boolean_fields = self._get_boolean_fields() # get boolean fields from processed schema
        else:
            raise ValueError("JSON data is empty")

    def _process_data(self):
        """Process JSON data into the schema."""
        data_items = self._json_data[0] if isinstance(self._json_data, list) else self._json_data # if json_data is list, get the first item
        for key, value in data_items.items():
            self.schema["properties"][key] = self._get_type(value)
            self.schema["required"].append(key)

    def _get_type(self, value: dict | list | str | None) -> dict:
        """Return the type of the given value."""
        if isinstance(value, dict):
            return {"type": "object", "properties": JsonSchemaGenerator(value)._get_properties()}
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
        
    def _get_properties(self) -> dict:
        return self.schema["properties"]

    def _get_required_fields(self) -> list:
        """Return the required fields."""
        return self.schema["required"]

    def _get_boolean_fields(self) -> dict:
        """Return the boolean fields."""
        return {key: value for key, value in self.schema["properties"].items() if value["type"] == "boolean"}
