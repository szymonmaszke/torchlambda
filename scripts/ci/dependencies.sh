#!/usr/bin/env sh

pip install -e . && pip install numpy torch torchvision
docker pull lambci/lambda:provided
