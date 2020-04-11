import collections
import itertools


def data(settings) -> str:
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
    return '"' + settings["input"]["name"] + '"'


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
            for field in settings["input"]["shape"]
            if isinstance(field, str)
        ]
    )


def data_type(settings) -> str:
    type_mapping = {
        "base64": "",
        "byte": "uint8_t",
        "char": "int8_t",
        "short": "int16_t",
        "int": "int32_t",
        "long": "int64_t",
        "float": "float",
        "double": "double",
    }
    return type_mapping[settings["input"]["type"]]


def data_func(settings) -> str:
    type_mapping = {
        "base64": "",
        "byte": "Integer",
        "char": "Integer",
        "short": "Integer",
        "int": "Integer",
        "long": "Int64",
        "float": "Double",
        "double": "Double",
    }
    return "As" + type_mapping[settings["input"]["type"]]


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


def torch_data_type(settings):
    type_mapping = {
        "base64": "torch::kUInt8",
        "byte": "torch::kUInt8",
        "char": "torch::kInt8",
        "short": "torch::kInt16",
        "int": "torch::kInt32",
        "long": "torch::kInt64",
        "float": "torch::kFloat32",
        "double": "torch::kFloat64",
    }
    return type_mapping[settings["input"]["type"]]


def inputs(settings) -> str:
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
        str(elem)
        if isinstance(elem, int)
        else 'json_view.GetInteger("{}")'.format(elem)
        for elem in settings["input"]["shape"]
    )


def aws_to_torch(settings, key: str) -> str:
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
        "bool": "torch::kInt8",
        "int": "torch::kInt32",
        "long": "torch::kInt64",
        "double": "torch::kFloat64",
    }

    if settings["return"][key] is None:
        return ""

    return type_mapping[settings["return"][key]["type"].lower()]


def torch_approximation(settings, key: str) -> str:
    """
    PyTorch has no `bool` type in libtorch hence we approximate one.

    Each item will be later static_casted to appropriate type if needed,
    which is essentially a no-op for for already correct types.

    Usually only `bool` will be casted (eventually other "hard-types" if
    the architecture is specific).

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        String specifying type, e.g. "int8_t"
    """
    type_mapping = {
        "bool": "int8_t",
        "int": "int32_t",
        "long": "int64_t",
        "double": "double",
    }

    if settings["return"][key] is None:
        return ""

    return type_mapping[settings["return"][key]["type"].lower()]


def operations_and_arguments(settings):
    """
    If return->result specified get names of operations to apply on output tensor.

    Merges return->result->operations and return->result->arguments into
    single string to input.

    return ->result->operations is required.

    Names of operations or arguments isn't verified and it may result in compilation
    error if user specifies unavailable tensor function.

    Current weak point in design, check if it can be improved and "safer".

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        string representation of number, e.g. "255.0"

    """

    def _add_namespace(operation):
        return "torch::{}".format(operation)

    def _operation_with_arguments(operation, *values):
        return "{}({})".format(
            _add_namespace(operation),
            ",".join(map(str, [value for value in values if value])),
        )

    def _no_arguments_multiple_operations(operations):
        output = _operation_with_arguments(operations[0], "output")
        for operation in operations[1:]:
            output = _operation_with_arguments(operation, output)
        return output

    def _wrap_in_list(value):
        if not isinstance(value, list):
            return [value]
        return value

    if settings["return"]["result"] is None:
        return ""

    if "code" in settings["return"]["result"]:
        return settings["return"]["result"]["code"]

    operations = settings["return"]["result"]["operations"]
    arguments = settings["return"]["result"]["arguments"]
    if arguments is None:
        if isinstance(operations, str):
            return "{}(output)".format(_add_namespace(operations))
        return _no_arguments_multiple_operations(operations)

    operations, arguments = _wrap_in_list(operations), _wrap_in_list(arguments)
    output = _operation_with_arguments(operations[0], "output", arguments[0])
    for operation, argument in itertools.zip_longest(operations[1:], arguments[1:]):
        output = _operation_with_arguments(operation, output, argument)
    return output


def aws_function(settings, key: str, array: bool) -> str:
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
    array: bool
        Whether prefix should be tailored to array output (`As`) or item (`With`)

    Returns
    -------
    str:
        "" or "As<type>" or "With<type>" AWS function name

    """

    prefix = "As" if array else "With"
    type_mapping = {
        "int": "Integer",
        "long": "Int64",
        "double": "Double",
    }

    if settings["return"][key] is None:
        return ""
    return prefix + type_mapping[settings["return"][key]["type"].lower()]


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


def model(settings) -> str:
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
    return '"' + settings["model"] + '"'
