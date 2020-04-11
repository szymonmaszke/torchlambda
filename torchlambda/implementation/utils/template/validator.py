import collections

import cerberus


class Validator(cerberus.Validator):
    def _validate_is_shorter(self, other: str, field, value):
        """Test whether one field (arguments) is shorter than other (operations).

        The rule's arguments are validated against this schema:
        {"type": "string"}
        """
        arguments_length = (
            1 if not isinstance(value, collections.Iterable) else len(value)
        )
        operations_length = (
            1 if isinstance(self.document[other], str) else len(self.document[other])
        )
        if arguments_length > operations_length:
            self._error(
                field,
                "More arguments provided in field: {} than in operations!".format(
                    field,
                ),
            )

    def _validate_broadcastable(self, shape_field: str, field, value):
        """Test whether one field (arguments) is shorter than other (operations).

        The rule's arguments are validated against this schema:
        {"type": "string"}
        """
        shapes = self.root_document["input"][shape_field]
        if len(value) != 1 or len(value) != len(shapes):
            self._error(
                field,
                "{} field's shape is not broadcastable to provided input shape: {}".format(
                    field, shapes
                ),
            )


def _is_not_dict(field, value, error):
    if isinstance(value, dict):
        error(field, "field cannot be an instance of dict")


# Fix validator
def get():
    return Validator(
        {
            "grad": {"type": "boolean", "default": False},
            "optimize": {"type": "boolean", "default": False},
            "validate_json": {"type": "boolean", "default": True},
            "model": {"type": "string", "default": "/opt/model.ptc", "empty": False},
            "input": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "default": "data", "empty": False},
                    "validate": {"type": "boolean", "default": True},
                    "type": {
                        "type": "string",
                        "allowed": [
                            "base64",
                            "byte",
                            "char",
                            "short",
                            "int",
                            "long",
                            "float",
                            "double",
                        ],
                        "required": True,
                    },
                    "shape": {
                        "type": "list",
                        "schema": {"type": ["string", "integer"]},
                        "required": True,
                        "minlength": 2,
                        "empty": False,
                    },
                    "validate_shape": {"type": "boolean", "default": True},
                    "cast": {
                        "type": "string",
                        "allowed": [
                            "byte",
                            "char",
                            "short",
                            "int",
                            "long",
                            "half",
                            "float",
                            "double",
                        ],
                        "nullable": True,
                        "default": None,
                    },
                    "divide": {"type": "number", "nullable": True, "default": None},
                },
            },
            "normalize": {
                "type": "dict",
                "nullable": True,
                "schema": {
                    "means": {
                        "required": True,
                        "broadcastable": "shape",
                        "type": "list",
                        "schema": {"type": "number"},
                    },
                    "stddevs": {
                        "required": True,
                        "broadcastable": "shape",
                        "type": "list",
                        "schema": {"type": "number"},
                    },
                },
                "default": None,
            },
            # Return can be either result, output or both
            "return": {
                "type": "dict",
                "required": True,
                "schema": {
                    "output": {
                        "type": "dict",
                        "nullable": True,
                        "schema": {
                            # Return only single item, not array
                            "name": {
                                "type": "string",
                                "default": "output",
                                "empty": False,
                            },
                            "type": {
                                "type": "string",
                                "allowed": ["int", "long", "double", "bool"],
                                "required": True,
                            },
                            "item": {"type": "boolean", "default": False},
                        },
                        "default": None,
                    },
                    "result": {
                        "type": "dict",
                        "nullable": True,
                        "schema": {
                            # Return only single item, not array
                            "name": {"type": "string", "default": "result"},
                            "type": {
                                "type": "string",
                                "allowed": ["int", "long", "double", "bool"],
                                "required": True,
                            },
                            "item": {"type": "boolean", "default": False},
                            "operations": {
                                "oneof": [
                                    {
                                        "type": "list",
                                        "schema": {"type": "string", "empty": False},
                                        "empty": False,
                                    },
                                    {"type": "string", "empty": False},
                                ],
                                "required": True,
                            },
                            "arguments": {
                                "is_shorter": "operations",
                                "check_with": _is_not_dict,
                                "empty": False,
                                "dependencies": "operations",
                                "nullable": True,
                                "default": None,
                            },
                        },
                        "default": None,
                    },
                },
            },
        }
    )
