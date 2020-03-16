#!/usr/bin/env bash

# Copy necessary dependencies from build

AWS_COMPONENTS="$1"
COMPILATION="$2"

CMAKE_ARGS=()
CMAKE_ARGS+=("-DBUILD_SHARED_LIBS=OFF")
CMAKE_ARGS+=("-DAWS_COMPONENTS=${AWS_COMPONENTS}")

echo "torchlambda:: Building AWS Lambda .zip package."
echo "torchlambda:: Compilation flags: ${COMPILATION}"
echo "torchlambda:: Final build arguments: ${CMAKE_ARGS[*]}"

mkdir build &&
  cd build &&
  cmake3 -E env CXXFLAGS="${COMPILATION}" cmake3 "${CMAKE_ARGS[@]}" .. &&
  cmake3 --build . --config Release &&
  make aws-lambda-package-torchlambda

printf "\ntorchlambda:: App size:\n\n"
du -sh /usr/local/build/torchlambda

printf "\ntorchlambda:: Zipped app size:\n\n"
du -sh /usr/local/build/torchlambda.zip
printf "\ntorchlambda:: Deployment finished successfully."
