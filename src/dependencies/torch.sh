#!/usr/bin/env bash

TORCH_RELEASE=7f73f1d
OP_LIST="/home/app/model.yaml"

git clone --recursive https://github.com/pytorch/pytorch.git
git reset --hard "${TORCH_RELEASE}"

# We are using cmake3 and python3 so replace all occurrences of it in the script
# Only python with space as it's used in two more places. No difference for cmake, consistency's sake
sed -i 's/cmake\ /cmake3\ /g' /home/app/dependencies/pytorch/scripts/build_mobile.sh
sed -i 's/python\ /python3\ /g' /home/app/dependencies/pytorch/scripts/build_mobile.sh

# Build args targeting AWS Lambda capabilities
BUILD_ARGS=()
BUILD_ARGS+=("-DBUILD_TEST=OFF")
BUILD_ARGS+=("-DBUILD_PYTHON=OFF")

BUILD_ARGS+=("-DUSE_NATIVE_ARCH=ON")
BUILD_ARGS+=("-DATEN_NO_TEST=ON")

BUILD_ARGS+=("-DUSE_MPI=OFF")
BUILD_ARGS+=("-DUSE_NUMPY=OFF")
BUILD_ARGS+=("-DUSE_ROCM=OFF")
BUILD_ARGS+=("-DUSE_NCCL=OFF")
BUILD_ARGS+=("-DUSE_NNPACK=OFF")
BUILD_ARGS+=("-DUSE_NUMA=OFF")
BUILD_ARGS+=("-DUSE_MKLDNN=OFF")
BUILD_ARGS+=("-DUSE_GLOO=OFF")
BUILD_ARGS+=("-DUSE_OPENMP=OFF")

if [ -f "${OP_LIST}" ]; then
  BUILD_ARGS+=("SELECTED_OP_LIST=/home/app/model.yaml")
fi

cd ./pytorch/scripts &&
  ./build_mobile.sh "${BUILD_ARGS[@]}" &&
  cd - || exit 1
