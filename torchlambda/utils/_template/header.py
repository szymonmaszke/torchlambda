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
        all(isinstance(x, int) for x in settings["inputs"]), "STATIC"
    )


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


def validate_data(settings) -> str:
    """
    Return #define VALIDATE_DATA if validate_json: True specified.

    If specified, data will be checked for correctness
    (only whether `data` field exists).

    If not, InvalidJson with appropriate text will be returned.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define VALIDATE_DATA"
    """
    return macro.conditional(settings["validate_data"], "VALIDATE_DATA")


def validate_inputs(settings) -> str:
    """
    Return #define VALIDATE_INPUTS if validate_inputs: True specified.

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
        Either "" or "#define VALIDATE_INPUTS"
    """
    return macro.conditional(settings["validate_inputs"], "VALIDATE_INPUTS")


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
