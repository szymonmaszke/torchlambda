#!/usr/bin/env sh

set -e # Crash if anything returns non-zero code

TORCH_VERSION=${1:-"latest"}
TIME_IN_SECONDS=${2:-7200}

# Global test run settings
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

IMAGE="szymonmaszke/torchlambda:$TORCH_VERSION"
SETTINGS="$DIR/settings.yaml"

TEST_CPP_SOURCE_FOLDER="$DIR/test_cpp_source_folder"
TEST_PACKAGE="$DIR/deployment.zip"
TEST_CODE="$DIR/test_code"
MODEL="$DIR/model.ptc"

RESPONSE="output.json"
PAYLOAD="payload.json"

# Run for each test case
START=$(date +%s)
i=0

while [ $(($(date +%s) - "$TIME_IN_SECONDS")) -lt "$START" ]; do
  # Insert test case specific values into settings
  OUTPUT="$SETTINGS" python "$DIR"/src/setup.py
  echo "Test $i :: Tested settings:"
  cat "$SETTINGS"

  # # Use test settings to create C++ code template
  echo "Test $i :: Creating source code from settings"
  torchlambda template --yaml "$SETTINGS" --destination "$TEST_CPP_SOURCE_FOLDER"

  # # Build code template into deployment package
  echo "Test $i :: Building source code"
  torchlambda build "$TEST_CPP_SOURCE_FOLDER" --destination "$TEST_PACKAGE" --image "$IMAGE"
  unzip -qq "$TEST_PACKAGE" -d "$TEST_CODE"

  # # Create example model
  MODEL="$MODEL" python "$DIR"/src/model.py
  echo "Test $i :: Model size:"
  du -sh "$MODEL"

  SETTINGS="$SETTINGS" OUTPUT="$PAYLOAD" python "$DIR"/src/payload.py
  echo "Test $i :: Payload size:"
  du -sh "$PAYLOAD"

  echo "Test $i :: Setting up server"

  timeout 30 docker run --rm -v \
    "$TEST_CODE":/var/task:ro,delegated -v \
    "$MODEL":/opt/model.ptc:ro,delegated \
    -i -e DOCKER_LAMBDA_USE_STDIN=1 \
    lambci/lambda:provided \
    torchlambda <"$PAYLOAD" >"$RESPONSE"

  echo "Test $i :: Validating received response"
  SETTINGS="$SETTINGS" RESPONSE="$RESPONSE" python "$DIR"/src/validate.py

  # Clean up
  echo "Test $i :: Cleaning up"
  rm -rf "$SETTINGS" "$TEST_CPP_SOURCE_FOLDER" "$TEST_PACKAGE" "$TEST_CODE" "$MODEL" "$PAYLOAD" "$RESPONSE"
  i=$((i + 1))
done
