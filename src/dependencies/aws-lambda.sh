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

git clone https://github.com/awslabs/aws-lambda-cpp &&
  cd aws-lambda-cpp &&
  cmake3 --build . --target install -- "-j${MAX_JOBS}"
