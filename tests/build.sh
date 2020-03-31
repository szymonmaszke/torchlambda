#!/usr/bin/env sh

TORCH_VERSION=$1
torchlambda . --no-run --pytorch-version "$TORCH_VERSION"
