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

# Build arguments and custom user defined args

BUILD_ARGS=()
BUILD_ARGS+=("-DCMAKE_BUILD_TYPE=Release")

BUILD_ARGS+=("-DBUILD_SHARED_LIBS=OFF")
BUILD_ARGS+=("-DENABLE_UNITY_BUILD=ON")
BUILD_ARGS+=("-DCUSTOM_MEMORY_MANAGEMENT=OFF")
BUILD_ARGS+=("-DCPP_STANDARD=17")

BUILD_ARGS+=("$@")

echo "- ALTorch: Cloning and building AWS C++ SDK..."
git clone --recursive https://github.com/aws/aws-sdk-cpp.git &&
  cd aws-sdk-cpp &&
  cmake3 --build . "${BUILD_ARGS[@]}" --target install -- "-j${MAX_JOBS}"
