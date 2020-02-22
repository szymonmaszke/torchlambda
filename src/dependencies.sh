#!/usr/bin/env bash

cd dependencies && ./aws.sh && ./torch.sh && cd - || exit
cp -r dependencies/pytorch/build_mobile/install/include ./
