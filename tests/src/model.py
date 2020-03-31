import torch

import torchvision
import utils

if __name__ == "__main__":
    args = utils.parse_args()
    model = getattr(torchvision.models, "model")(pretrained=False)
    model.eval()

    example = torch.randn(1, 3, 64, 64)
    script_model = torch.jit.trace(model, example)

    script_model.save("model.ptc")
