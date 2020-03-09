#!/usr/bin/env bash

cd dependencies && ./aws-lambda.sh && ./aws-sdk.csh && ./torch.sh && cd - || exit
cp -r dependencies/pytorch/build_mobile/install/include ./
