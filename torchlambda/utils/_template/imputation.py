def data_field(settings) -> str:
    """
    Impute name of field containing base64 encoded data.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        "name_of_data_field"
    """
    return '"' + settings["data_field"] + '"'


def fields(settings) -> str:
    """
    Impute name of fields (if any) specifying tensor shape during request.

    Fields can be empty if tensor shape is known beforehand
    (STATIC macro defined, see `header.static` function).

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        "field1", "field2", ..., "fieldN"
    """
    return ", ".join(
        [
            '"' + field + '"'
            for field in settings["input_shape"]
            if isinstance(field, str)
        ]
    )


def normalize(settings, key: str) -> str:
    """
    Impute normalization values if any.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict
    key : str
        Name of YAML settings field (either means or stddevs) to be imputed

    Returns
    -------
    str:
        "" or "value1, value2, value3"
    """
    if settings["normalize"] is None:
        return ""
    return ", ".join(map(str, settings["normalize"][key]))


def input_shape(settings) -> str:
    """
    Impute input shapes.

    Shapes may be name of fields passed during request (dynamic input shape)
    or integers (static input shape) or mix of both.

    If field is a name (string), it will be transformed to `json_view.GetInteger(name)`.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        String like "1, 3, json_view.GetInteger("width"), json_view.GetInteger("height")"
    """
    return ", ".join(
        str(elem) if isinstance(elem, int) else "json_view.GetInteger({})".format(elem)
        for elem in settings["input_shape"]
    )


def cast(settings) -> str:
    """
    Impute libtorch specific type from user provided "human-readable" form.

    See `type_mapping` in source code for exact mapping.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        String specifying type, e.g. "torch::kFloat16"
    """
    type_mapping = {
        "byte": "torch::kUInt8",
        "char": "torch::kInt8",
        "short": "torch::kInt16",
        "int": "torch::kInt32",
        "long": "torch::kInt64",
        "half": "torch::kFloat16",
        "float": "torch::kFloat32",
        "double": "torch::kFloat64",
    }

    return type_mapping[settings["cast"].lower()]


def divide(settings) -> str:
    """
    Impute value by which casted tensor will be divided.

    If user doesn't want to cast tensor, he should simply specify `1`,
    though it won't be used too often.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        string representation of number, e.g. "255.0"

    """
    return str(settings["divide"])


def result_operation(settings) -> str:
    """
    If return->result specified get name of operation to apply on output tensor.

    This operation is required as it creates "result" from operation.

    Name of the operation isn't verified and it may result in compilation error
    if user specifies unavailable tensor function.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        string representation of number, e.g. "255.0"

    """
    if settings["return"]["result"] is None:
        return ""
    return settings["return"]["result"]["operation"]


def aws_function(settings, key: str) -> str:
    """
    Internal imputation specifying one of AWS SDK functions based on type.

    This function specifies which AWS SDK function will be used to create
    JSONValue (either as single item to return or as part of array to return).

    Looked for in return->output and return->result settings and returns one or both
    depending on which is specified.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict
    key : str
        Name of field to look for in type (either "output" or "result")

    Returns
    -------
    str:
        "" or "With<type>" AWS function name

    """
    type_mapping = {
        "bool": "Bool",
        "int": "Integer",
        "long": "Int64",
        "double": "Double",
    }
    if settings["return"][key] is None:
        return ""
    return "With" + type_mapping[settings["return"][key]["type"].lower()]


def field_if_exists(settings, key: str, name: str) -> str:
    """
    Return value of nested fields if those are specified.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict
    key : str
        Name of field to look for in type (either "output" or "result")
    name: str
        Name of field to look for in one of "output" or "result"

    Returns
    -------
    str:
        "" or value provided in field

    """
    if settings["return"][key] is None:
        return ""
    return settings["return"][key][name]


def model_path(settings) -> str:
    """
    Return path to model specified by settings.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        "/path/to/model"

    """
    return '"' + settings["model_path"] + '"'
