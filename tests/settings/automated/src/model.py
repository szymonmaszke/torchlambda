import os
import random

import torch
import torchvision
import yaml

import utils


def create_model():
    possible_models = [
        "shufflenet_v2_x1_0",
        "resnet18",
        "mobilenet_v2",
        "mnasnet1_0",
        "mnasnet1_3",
    ]

    settings = utils.load_settings()
    model_name = random.choice(possible_models)
    print("Test:: Model: {}".format(model_name))
    model = getattr(torchvision.models, model_name)()

    script_model = torch.jit.script(model)
    script_model.save(os.environ["MODEL"])

    settings["model_name"] = model_name
    with open(os.environ["SETTINGS"], "w") as file:
        yaml.dump(settings, file, default_flow_style=False)


if __name__ == "__main__":
    create_model()
