#!/usr/bin/env bash

set -e # Crash if anything returns non-zero code

TORCH_VERSION=${1:-"latest"}

# Global test run settings
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Where performance analysis will be saved
DATA="$DIR/data"
mkdir -p "$DATA"

IMAGE="szymonmaszke/torchlambda:$TORCH_VERSION"

TEST_CPP_SOURCE_FOLDER="$DIR/test_cpp_source_folder"
TEST_PACKAGE="$DIR/deployment.zip"
TEST_CODE="$DIR/test_code"
MODEL="$DIR/model.ptc"

RESPONSE="output.json"
PAYLOAD="payload.json"

# Run for each test case
FINAL_DATA="analysis"

SECS=7200
ENDTIME=$(($(date +%s) + SECS))
START=$(date +%s)

while [ $(date +%s) -lt $ENDTIME ]; do
  # Insert test case specific values into settings
  OUTPUT="$DATA/$i.yaml" python "$DIR"/src/setup.py
  echo "Test $i :: Tested settings:"
  cat "$DATA/$i.yaml"

  # # Use test settings to create C++ code template
  echo "Test $i :: Creating source code from settings"
  torchlambda template --yaml "$DATA/$i.yaml" --destination "$TEST_CPP_SOURCE_FOLDER"

  # # Build code template into deployment package
  echo "Test $i :: Building source code"
  torchlambda build "$TEST_CPP_SOURCE_FOLDER" --destination "$TEST_PACKAGE" --image "$IMAGE"
  unzip -qq "$TEST_PACKAGE" -d "$TEST_CODE"

  # # Create example model
  MODEL="$MODEL" SETTINGS="$DATA/$i.yaml" python "$DIR"/src/model.py
  echo "Test $i :: Model size:"
  du -sh "$MODEL"

  SETTINGS="$DATA/$i.yaml" OUTPUT="$PAYLOAD" python "$DIR"/src/payload.py
  echo "Test $i :: Payload size:"
  du -sh "$PAYLOAD"

  echo "Test $i :: Setting up server"

  timeout 30 docker run --rm -v \
    "$TEST_CODE":/var/task:ro,delegated -v \
    "$MODEL":/opt/model.ptc:ro,delegated \
    -i -e DOCKER_LAMBDA_USE_STDIN=1 \
    lambci/lambda:provided \
    torchlambda <"$PAYLOAD" >"$RESPONSE" 2>"temp"

  # Remove colored output from lambci
  sed 's/\x1b\[[0-9;]*m//g' "temp" | tail -n 1 >"temp2"

  echo "Test $i :: Validating received response"
  SETTINGS="$DATA/$i.yaml" RESPONSE="$RESPONSE" python "$DIR"/src/validate.py

  echo "Test $i :: Adding time measurements"
  SETTINGS="$DATA/$i.yaml" DATA="temp2" python "$DIR"/src/process.py

  # Clean up
  echo "Test $i :: Cleaning up"
  rm -rf "temp" "temp2" "$TEST_CPP_SOURCE_FOLDER" "$TEST_PACKAGE" "$TEST_CODE" "$MODEL" "$PAYLOAD" "$RESPONSE"
  i=$((i + 1))
done

echo "Test :: Creating statistics: $FINAL_DATA"
OUTPUT="$FINAL_DATA" DATA="$DATA" python "$DIR"/src/gather.py
rm -rf "$DATA"
