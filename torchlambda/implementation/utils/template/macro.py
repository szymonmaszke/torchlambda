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


def key(dictionary, key: str, mapping: typing.Dict = None) -> str:
    """
    Return C++ macro-string "#define name value" based on provided key.

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
        "#define name value" or "#define name value"
    """
    value = dictionary.get(key, None)
    if value is not None:
        if mapping is not None:
            value = mapping[value]
        return define(key.upper(), value)
    return ""


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
