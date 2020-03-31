#!/usr/bin/env sh

TORCH_VERSION=$1
torchlambda build . --no-run --pytorch-version "$TORCH_VERSION"
