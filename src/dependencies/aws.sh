#!/usr/bin/env bash

git clone https://github.com/awslabs/aws-lambda-cpp &&
  cd aws-lambda-cpp &&
  mkdir -p build &&
  cd build &&
  cmake3 .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=./install &&
  make && make install
