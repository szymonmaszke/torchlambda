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

CMAKE_ARGS=()

CMAKE_ARGS+=("-DENABLE_TESTING=OFF")
CMAKE_ARGS+=("-DBUILD_ONLY=core")

CMAKE_ARGS+=("-DENABLE_TESTING=OFF")

CMAKE_ARGS+=("-DMINIMIZE_SIZE=ON")

CMAKE_ARGS+=("-DCUSTOM_MEMORY_MANAGEMENT=OFF")
CMAKE_ARGS+=("-DCPP_STANDARD=17")

CMAKE_ARGS+=("$@")

if [ -x "$(command -v ninja)" ]; then
  CMAKE_ARGS+=("-GNinja")
fi

CMAKE_ARGS+=("-DBUILD_SHARED_LIBS=OFF")

echo "torchlambda:: AWS C++ SDK build arguments:"
echo "${CMAKE_ARGS[@]}"

echo "torchlambda:: Cloning and building AWS C++ SDK..."
git clone https://github.com/aws/aws-sdk-cpp.git &&
  cd aws-sdk-cpp &&
  mkdir -p build &&
  cd build &&
  cmake3 .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local "${CMAKE_ARGS[@]}" &&
  cmake3 --build . --target install -- "-j${MAX_JOBS}"

echo "torchlambda:: AWS C++ SDK built successfully."
