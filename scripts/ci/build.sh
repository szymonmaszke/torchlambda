#!/usr/bin/env sh

TORCH_VERSION=${1:-"latest"}
torchlambda build . --no-run --pytorch-version "$TORCH_VERSION" --image "szymonmaszke/torchlambda:$TORCH_VERSION"
