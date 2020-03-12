#!/usr/bin/env bash

# Original source:
# https://github.com/pytorch/pytorch/blob/master/scripts/build_mobile.sh#L63

if [ -z "$MAX_JOBS" ]; then
  if [ "$(uname)" == 'Darwin' ]; then
    MAX_JOBS=$(sysctl -n hw.ncpu)
  else
    MAX_JOBS=$(nproc)
  fi
else
  MAX_JOBS=1
fi

if [ -x "$(command -v ninja)" ]; then
  CMAKE_ARGS+=("-GNinja")
fi

git clone https://github.com/awslabs/aws-lambda-cpp.git &&
  cd aws-lambda-cpp &&
  mkdir -p build &&
  cd build &&
  cmake3 .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=./install &&
  cmake3 --build . --target install -- "-j${MAX_JOBS}"
