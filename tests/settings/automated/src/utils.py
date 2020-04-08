import argparse
import json
import sys
import typing


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("test", help="Specific JSON test settings used")

    return parser.parse_args()


def load_test(args) -> typing.Dict:
    with open(args.test, "r") as file:
        try:
            return json.load(file)
        except Exception as error:
            print("Test error:: JSON file loaded uncorrectly.")
            print(error)
            sys.exit(1)
