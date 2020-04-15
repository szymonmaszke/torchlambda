import pathlib
import sys
import typing

import yaml

from . import general, utils


@general.message("reading YAML settings.")
def read_settings(args) -> typing.Dict:
    """
    Read user provided YAML settings.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    Returns
    -------
        Dictionary containing settings to create template
    """
    with open(args.yaml, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as error:
            print("torchlambda:: Error during user settings parsing:")
            print(error)
            sys.exit(1)


@general.message("validating YAML settings.")
def validate(validator, settings: typing.Dict) -> None:
    """
    Validate user provided YAML settings.

    Uses custom validator, see `utils.template/validator.py` for
    exact validation scheme.

    Parameters
    ----------
    validator : cerberus.Validator
        Cerberus scheme validator
    settings : typing.Dict
        YAML parsed to dict

    """
    if not validator.validate(settings, normalize=True):
        print("torchlambda:: Error during YAML validation:", file=sys.stderr)
        print(yaml.dump(validator.errors), file=sys.stderr)
        sys.exit(1)


@general.message("creating .cpp source from YAML template.")
def create_source(settings: typing.Dict) -> str:
    """
    Create .cpp source code from template and settings

    Values are imputed using `format` to `main.cpp`.
    Each field is either a header (#define NAME <value>, <value> optional)
    or is directly imputed into source code.

    First case and all needed processing is located in `utils.template.header`,
    second case and all needed processing is located in `utils.template.imputation`

    `template/main.cpp` template file uses double curly brackets ({{}}) where normal
    C++ brackets are used in order to be compatible with `str.format`, see
    this: https://stackoverflow.com/questions/5466451/how-can-i-print-literal-curly-brace-characters-in-python-string-and-also-use-fo
    for some info.

    **DESCRIPTION OF HEADER FIELDS**:

        - STATIC - whether all shapes are static (e.g. no
        input dimension is dependent on value passed in request as field).
        True if `input_shape` only has integers (fixed input shape).

        - VALIDATE_INPUTS - whether fields provided in INPUT_SHAPE should be
        checked for correctness (they exist and are of integer type).
        Default: True

        - NO_GRAD - whether PyTorch's gradient should be disabled.
        Usually yes as AWS Lambda is mainly used for inference
        Default: True

        - CAST - to which type should the tensor be casted after creation from
        base64 encoded data (by default it's unsigned char which is rarely useful).
        Default: float

        - NORMALIZE - whether normalize input using NORMALIZE_MEANS and NORMALIZE_STDDEVS
        Used mainly for image inference.
        Default: False

        - DIVIDER - value by which input tensor will be divided after casting
        to CAST.
        Default: 255 (to bring `unsigned char` to `[0,1]` range, useful for image inference)

        - RETURN_OUTPUT - whether to return output as array.
        Exclusive with RETURN_OUTPUT_ITEM

        - RETURN_OUTPUT_ITEM - whether to return output as single item.
        Exclusive with RETURN_OUTPUT

        - RETURN_RESULT - whether to return result as array.
        Exclusive with RETURN_RESULT_ITEM

        - RETURN_RESULT_ITEM - whether to return output as single item.
        Exclusive with RETURN_RESULT

    **DESCRIPTION OF DIRECTLY IMPUTED FIELDS**:

        - DATA - Name of field providing data in request

        - FIELDS - Names (if any) of provided non-static fields

        - NORMALIZE_MEANS - Means to use for normalization (if any)

        - NORMALIZE_STDDEVS - Standard deviations to use for normalization (if any)

        - INPUTS - Input shapes used for reshape of tensor (including batch dimension)

        - IF RETURN_RESULT OR RETURN_RESULT_ITEM DEFINED:

            - OPERATIONS_AND_ARGUMENTS - Operations with arguments (if any) to apply over
            outputted tensor to create result.
            Mix of "operations" and "arguments" fields

        - IF RETURN_OUTPUT OR RETURN_OUTPUT_ITEM DEFINED:

            - AWS_OUTPUT_FUNCTION - Internal AWS SDK JsonValue function like WithInteger.
            Based on RETURN_OUTPUT_TYPE

        - IF RETURN_RESULT OR RETURN_RESULT_ITEM DEFINED:

            - AWS_RESULT_FUNCTION - Internal AWS SDK JsonValue function like WithInteger.
            Based on RETURN_RESULT_TYPE

        - IF RETURN_OUTPUT OR RETURN_OUTPUT_ITEM DEFINED:

            - OUTPUT_NAME - Key of returned JSON
            - OUTPUT_TYPE - Type  of item of returned JSON

        - IF RETURN_RESULT OR RETURN_RESULT_ITEM DEFINED:

            - RESULT_NAME - Key of returned JSON
            - RESULT_TYPE - Type  of item of returned JSON

    Parameters
    ----------
    settings : typing.Dict
        YAML parsed to dict

    Returns
    -------
    str:
        Source represented as string
    """
    cwd = pathlib.Path(__file__).absolute().parent.parent
    with open(cwd / "templates/settings/main.cpp") as file:
        return file.read().format(
            # Top level defines
            STATIC=utils.template.header.static(settings),
            GRAD=utils.template.header.grad(settings),
            OPTIMIZE=utils.template.header.optimize(settings),
            VALIDATE_JSON=utils.template.header.validate_json(settings),
            BASE64=utils.template.header.base64(settings),
            VALIDATE_FIELD=utils.template.header.validate_field(settings),
            VALIDATE_SHAPE=utils.template.header.validate_shape(settings),
            NORMALIZE=utils.template.header.normalize(settings),
            CAST=utils.template.header.cast(settings),
            DIVIDE=utils.template.header.divide(settings),
            RETURN_OUTPUT=utils.template.header.return_output(settings),
            RETURN_OUTPUT_ITEM=utils.template.header.return_output_item(settings),
            RETURN_RESULT=utils.template.header.return_result(settings),
            RETURN_RESULT_ITEM=utils.template.header.return_result_item(settings),
            # Direct insertions
            DATA=utils.template.imputation.data(settings),
            FIELDS=utils.template.imputation.fields(settings),
            DATA_TYPE=utils.template.imputation.data_type(settings),
            DATA_FUNC=utils.template.imputation.data_func(settings),
            NORMALIZE_MEANS=utils.template.imputation.normalize(settings, key="means"),
            NORMALIZE_STDDEVS=utils.template.imputation.normalize(
                settings, key="stddevs"
            ),
            TORCH_DATA_TYPE=utils.template.imputation.torch_data_type(settings),
            INPUTS=utils.template.imputation.inputs(settings),
            OUTPUT_CAST=utils.template.imputation.aws_to_torch(settings, "output"),
            RESULT_CAST=utils.template.imputation.aws_to_torch(settings, "result"),
            OPERATIONS_AND_ARGUMENTS=utils.template.imputation.operations_and_arguments(
                settings
            ),
            AWS_OUTPUT_FUNCTION=utils.template.imputation.aws_function(
                settings, key="output", array=True,
            ),
            AWS_RESULT_FUNCTION=utils.template.imputation.aws_function(
                settings, key="result", array=True,
            ),
            AWS_OUTPUT_ITEM_FUNCTION=utils.template.imputation.aws_function(
                settings, key="output", array=False
            ),
            AWS_RESULT_ITEM_FUNCTION=utils.template.imputation.aws_function(
                settings, key="result", array=False
            ),
            TORCH_OUTPUT_TYPE=utils.template.imputation.torch_approximation(
                settings, key="output"
            ),
            OUTPUT_TYPE=utils.template.imputation.field_if_exists(
                settings, key="output", name="type"
            ),
            TORCH_RESULT_TYPE=utils.template.imputation.torch_approximation(
                settings, key="result"
            ),
            RESULT_TYPE=utils.template.imputation.field_if_exists(
                settings, key="result", name="type"
            ),
            OUTPUT_NAME=utils.template.imputation.field_if_exists(
                settings, key="output", name="name"
            ),
            RESULT_NAME=utils.template.imputation.field_if_exists(
                settings, key="result", name="name"
            ),
            MODEL_PATH=utils.template.imputation.model(settings),
        )


def save(source: str, args) -> None:
    """
    Save created source file to specified destination.

    All needed folders will be created if necessary.

    Parameters
    ----------
    source : str
        String representation of C++ deployment source code
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    """
    destination = pathlib.Path(args.destination).absolute()
    destination.mkdir(parents=True, exist_ok=True)
    with open(destination / "main.cpp", "w") as file:
        file.write(source)


def create_template(args) -> None:
    """
    Create and save template from user provided settings.

    Acts as an entrypoint if user specifies --yaml flag in `torchlambda scheme`
    command.

    Parameters
    ----------
    args : dict-like
        User provided arguments parsed by argparse.ArgumentParser instance.

    """
    settings = read_settings(args)
    validator = utils.template.validator.get()
    validate(validator, settings)
    settings = validator.normalized(settings)

    source = create_source(settings)
    save(source, args)
