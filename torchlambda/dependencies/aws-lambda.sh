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

CMAKE_ARGS=()

if [ -x "$(command -v ninja)" ]; then
  CMAKE_ARGS+=("-GNinja")
fi

CMAKE_ARGS+=("-DBUILD_SHARED_LIBS=OFF")

echo "torchlambda:: AWS Lambda C++ Runtime build arguments:"
echo "${CMAKE_ARGS[@]}"

echo "torchlambda:: Cloning and building AWS Lambda C++ Runtime..."
git clone https://github.com/awslabs/aws-lambda-cpp.git &&
  cd aws-lambda-cpp &&
  mkdir -p build &&
  cd build &&
  cmake3 .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local "${CMAKE_ARGS[@]}" &&
  cmake3 --build . --target install -- "-j${MAX_JOBS}"

echo "torchlambda:: AWS Lambda C++ Runtime built successfully."
