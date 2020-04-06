import typing


def define(name: str, value: str = "") -> str:
    """
    Return C++ macro-string #define name value

    Used for header defines.

    Parameters
    ----------
    name : str
        Name of macro to be defined
    value : str, optional
        Value of defined macro (if any),

    Returns
    -------
    str:
        "#define name" or "#define name value"
    """
    return "#define {} {}".format(name, value)


def conditional(condition: bool, name: str, value: typing.Any = "") -> str:
    """
    Return C++ macro-string "#define name value" if condition is True.

    Used for header defines based on user-provided setting.

    Parameters
    ----------
    name : str
        Name of macro to be defined
    value : str, optional
        Value of defined macro (if any),

    Returns
    -------
    str:
        "#define name" or "#define name value"
    """
    if condition:
        return define(name, value)
    return ""
