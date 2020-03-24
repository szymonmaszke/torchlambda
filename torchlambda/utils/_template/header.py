from . import macro


def static(settings) -> str:
    """
    Return #define STATIC if all input_shape fields are integer.

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
        all(isinstance(x, int) for x in settings["input_shape"]), "STATIC"
    )


def check_fields(settings) -> str:
    """
    Return #define CHECK_FIELDS if check_fields: True specified.

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
        Either "" or "#define CHECK_FIELDS"
    """
    return macro.conditional(settings["check_fields"], "CHECK_FIELDS")


def no_grad(settings) -> str:
    """
    Return #define NO_GRAD if no_grad: True specified.

    If specified, libtorch's grad addition to ATen will be turned off.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define NO_GRAD"
    """
    return macro.conditional(settings["no_grad"], "NO_GRAD")


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


def result_operation_dim(settings):
    """
    Return #define RESULT_OPERATION_DIM <value> if field return->result->dim is specified.

    Will apply RESULT_OPERATION across RESULT_OPERATION_DIM <value>
    (e.g. across first dimension) if RESULT_OPERATION_DIM <value< specified as
    header.

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Either "" or "#define RESULT_OPERATION_DIM"
    """
    dim_exists = settings["return"]["result"] and settings["return"]["result"]["dim"]
    return macro.conditional(
        dim_exists,
        "RESULT_OPERATION_DIM",
        settings["return"]["result"]["dim"] if dim_exists else None,
    )
