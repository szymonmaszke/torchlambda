import os
import pathlib
import sys
import typing

import yaml

import torchlambda


def load_settings() -> typing.Dict:
    with open(pathlib.Path(os.environ["SETTINGS"]).absolute(), "r") as file:
        try:
            return torchlambda.implementation.utils.template.validator.get().normalized(
                yaml.safe_load(file)
            )
        except yaml.YAMLError as error:
            print("Test error:: Error during user settings loading.")
            print(error)
            sys.exit(1)
