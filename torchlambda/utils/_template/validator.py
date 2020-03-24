import cerberus


def get():
    return cerberus.Validator(
        {
            "data_field": {"type": "string", "default": "data"},
            "model_path": {"type": "string", "default": "/opt/model.ptc"},
            "input_shape": {
                "type": "list",
                "schema": {"type": ["string", "integer"]},
                "required": True,
                "minlength": 2,
            },
            "check_fields": {"type": "boolean", "default": True},
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
                "default": "float",
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
                            "item": {"type": "boolean"},
                            "name": {"type": "string", "default": "output"},
                            "type": {
                                "type": "string",
                                "allowed": ["bool", "int", "long", "double"],
                                "required": True,
                            },
                        },
                        "default": None,
                    },
                    "result": {
                        "type": "dict",
                        "nullable": True,
                        "schema": {
                            # Return only single item, not array
                            "item": {"type": "boolean"},
                            "name": {"type": "string", "default": "result"},
                            "type": {
                                "type": "string",
                                "allowed": ["bool", "int", "long", "double"],
                                "required": True,
                            },
                            # Operation is required as it changes output
                            # And creates result
                            "operation": {"type": "string", "required": True},
                            "dim": {"type": "integer", "dependencies": "operation"},
                        },
                        "default": None,
                    },
                },
            },
            "no_grad": {"type": "boolean", "default": True},
            "normalize": {
                "type": "dict",
                "nullable": True,
                "schema": {
                    "means": {
                        "type": "list",
                        "schema": {"type": "number"},
                        "default": [0.485, 0.456, 0.406],
                    },
                    "stddevs": {
                        "type": "list",
                        "schema": {"type": "number"},
                        "default": [0.229, 0.224, 0.225],
                    },
                },
                "default": None,
            },
            "divide": {"type": "number", "default": 255},
        }
    )
