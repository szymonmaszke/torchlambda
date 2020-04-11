from . import macro


def static(settings) -> str:
    """
    Return #define STATIC if all inputs fields are integer.

    If specified, no field checks will be performed during request to
    Lambda function.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define STATIC"
    """
    return macro.conditional(
        all(isinstance(x, int) for x in settings["input"]["shape"]), "STATIC"
    )


def grad(settings) -> str:
    """
    Return #define GRAD if grad: True specified.

    If specified, libtorch's grad addition to ATen will be turned on.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define GRAD"
    """
    return macro.conditional(settings["grad"], "GRAD")


def optimize(settings) -> str:
    """
    Return #define GRAD if grad: True specified.

    If specified, libtorch's grad addition to ATen will be turned on.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define GRAD"
    """
    return macro.conditional(settings["optimize"], "OPTIMIZE")


def validate_json(settings) -> str:
    """
    Return #define VALIDATE_JSON if validate_json: True specified.

    If specified, it will be validated if JSON was parsed successfully.
    If not, InvalidJson with appropriate text will be returned.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define VALIDATE_JSON"
    """
    return macro.conditional(settings["validate_json"], "VALIDATE_JSON")


def base64(settings) -> str:
    """
    Return #define BASE64 if input->type is equal to base64.

    If specified, it is assumed data is in base64 string format and will be decoded
    in handler. In this case input_type IS NOT USED and data type will be
    unsigned int 8 upon creation (which can be optionally casted).

    If not, it is assumed data will be a flat array of specified by user via
    input_type.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define BASE64"
    """
    return macro.conditional(settings["input"]["type"] == "base64", "BASE64")


def validate_field(settings) -> str:
    """
    Return #define VALIDATE_FIELD if validate: True specified.

    If specified, data will be checked for correctness
    (whether `data` field exists and whether it's type is string or array).

    If not, InvalidJson with appropriate text will be returned.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define VALIDATE_FIELD"
    """
    return macro.conditional(settings["input"]["validate"], "VALIDATE_FIELD")


def validate_shape(settings) -> str:
    """
    Return #define VALIDATE_SHAPE if validate_inputs: True specified.

    If specified, input fields will be checked (if any exist).
    All of them will be checked for existence and whether their type
    is integer.

    If not, InvalidJson with appropriate text will be returned.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define VALIDATE_SHAPE"
    """
    return macro.conditional(settings["input"]["validate_shape"], "VALIDATE_SHAPE")


def normalize(settings) -> str:
    """
    Return #define NORMALIZE if normalize: True specified.

    Will normalize image-like tensor across channels using
    torch::data::transforms::Normalize<>.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define NORMALIZE"
    """
    return macro.conditional(settings["normalize"], "NORMALIZE")


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

    return macro.key(settings["input"], key="cast", mapping=type_mapping,)


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
    return macro.key(settings["input"], key="divide")


def return_output(settings):
    """
    Return #define RETURN_OUTPUT if field return->output is specified.

    Will return output from neural network as JSON array of specified
    OUTPUT_TYPE if macro defined.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define RETURN_OUTPUT"
    """
    return macro.conditional(
        settings["return"]["output"] and not settings["return"]["output"]["item"],
        "RETURN_OUTPUT",
    )


def return_output_item(settings):
    """
    Return #define RETURN_OUTPUT if field return->output->item is specified.

    Will return output from neural network as single element of specified
    OUTPUT_TYPE if macro defined.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define RETURN_OUTPUT_ITEM"
    """
    return macro.conditional(
        settings["return"]["output"] and settings["return"]["output"]["item"],
        "RETURN_OUTPUT_ITEM",
    )


def return_result(settings):
    """
    Return #define RETURN_RESULT if field return->result is specified.

    Will return modified by RESULT_OPERATION output from neural network
    as JSON array of specified RESULT_TYPE if macro defined.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define RETURN_RESULT"
    """
    return macro.conditional(
        settings["return"]["result"] and not settings["return"]["result"]["item"],
        "RETURN_RESULT",
    )


def return_result_item(settings):
    """
    Return #define RETURN_RESULT_ITEM if field return->result->item is specified.

    Will return modified by RESULT_OPERATION output from neural network
    as single item of specified RESULT_TYPE if macro defined

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define RETURN_RESULT_ITEM"
    """
    return macro.conditional(
        settings["return"]["result"] and settings["return"]["result"]["item"],
        "RETURN_RESULT_ITEM",
    )
