import argparse
import functools
import itertools
import pathlib
import zipfile
from datetime import datetime

import numpy as np
import pandas as pd


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "directory", help="Directory containing performance file created by analysis",
    )

    parser.add_argument(
        "output", help="Markdown file to output performance analysis combinations.",
    )

    return parser.parse_args()


def duration_mapping(name: str):
    return {"init": 0, "duration": 1, "billed": 2}[name]


def matrix_mapping(name: str):
    mapping = {
        key: index
        for index, key in enumerate(
            ("grad", "type", "payload", "model_name", "normalize", "return")
        )
    }
    return mapping[name]


def sum_of_trials(args):
    def gather_all(key: str):
        return np.stack(
            [np.load(path)[key] for path in pathlib.Path(args.directory).glob("*.npz")]
        ).sum(axis=0)

    trials, occurrences = gather_all("data"), gather_all("occurrences")
    return trials, occurrences


def axis_description(name: str):
    mapping = {
        "grad": [True, False],
        "type": ["base64", "byte", "char", "short", "int", "long", "float", "double",],
        "payload": [
            "256x256",
            "256x512",
            "512x256",
            "512x512",
            "64x64",
            "128x64",
            "64x128",
            "128x128",
        ],
        "model_name": [
            "shufflenet_v2_x1_0",
            "resnet18",
            "mobilenet_v2",
            "mnasnet1_0",
            "mnasnet1_3",
        ],
        "normalize": [True, False],
        "return": ["output", "result", "result+output"],
    }

    return mapping[name]


def get_results(trials, occurrences, rows, columns, duration):
    def _reduce(matrix):
        return np.sum(
            matrix,
            axis=tuple(
                i
                for i in range(len(matrix.shape) - 1)
                if i not in (matrix_mapping(rows), matrix_mapping(columns))
            ),
        )[:, :, duration_mapping(duration)]

    return _reduce(trials) / _reduce(occurrences)


def header() -> str:
    with open("header.md", "r") as f:
        return f.read() + "\n\n"


if __name__ == "__main__":
    args = parse()
    trials, occurrences = sum_of_trials(args)
    fields = ("grad", "type", "payload", "model_name", "normalize", "return")
    times = ("init", "duration", "billed")

    markdown = header()
    for time, (row, column) in itertools.product(
        times, itertools.combinations(fields, 2)
    ):
        markdown += "\n\n## {}: {} x {}\n\n".format(time, row, column)

        result_matrix = get_results(trials, occurrences, row, column, time)
        df = pd.DataFrame(
            data=result_matrix,
            index=axis_description(row),
            columns=axis_description(column),
        )

        markdown += df.to_markdown()

    markdown += "\n\n _This file was auto-generated on {}_".format(
        datetime.today().strftime("%Y-%m-%d-%H:%M:%S")
    )

    with open(args.output, "w") as f:
        f.write(markdown)
