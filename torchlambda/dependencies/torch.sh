#!/usr/bin/env bash

TORCH_RELEASE=7f73f1d
OP_LIST="/home/app/model.yaml"

# Build args targeting AWS Lambda capabilities
BUILD_ARGS=()
BUILD_ARGS+=("-DBUILD_PYTHON=OFF")

BUILD_ARGS+=("-DUSE_MPI=OFF")
BUILD_ARGS+=("-DUSE_NUMPY=OFF")
BUILD_ARGS+=("-DUSE_ROCM=OFF")
BUILD_ARGS+=("-DUSE_NCCL=OFF")
BUILD_ARGS+=("-DUSE_NUMA=OFF")
BUILD_ARGS+=("-DUSE_MKLDNN=ON")
BUILD_ARGS+=("-DUSE_GLOO=OFF")
BUILD_ARGS+=("-DUSE_OPENMP=OFF")

BUILD_ARGS+=("$@")

# Display gathered arguments
printf "\n\ntorchlambda:: Libtorch build arguments:\n\n"
echo "${BUILD_ARGS[@]}"

# Export selected operations if provided
if [ -f "${OP_LIST}" ]; then
  export SELECTED_OP_LIST="${OP_LIST}"
  printf "torchlambda:: Building with following customized operations:\n\n"
  cat "$OP_LIST"
fi

echo "torchlambda:: Cloning and building Libtorch..."
git clone --recursive https://github.com/pytorch/pytorch.git
echo "- torchlambda:: Resetting PyTorch to official 1.4.0 release..."
cd pytorch && git reset --hard "${TORCH_RELEASE}" && cd - || exit 1

# We are using cmake3 and python3 so replace all occurrences of it in the script
# Only python with space as it's used in two more places. No difference for cmake, consistency's sake
sed -i 's/cmake\ /cmake3\ /g' /home/app/dependencies/pytorch/scripts/build_mobile.sh
sed -i 's/python\ /python3\ /g' /home/app/dependencies/pytorch/scripts/build_mobile.sh

./pytorch/scripts/build_mobile.sh "${BUILD_ARGS[@]}"

echo "torchlambda:: Libtorch built successfully."