#!/usr/bin/env sh

set -e

# Global test run settings
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

TIME_IN_SECONDS=1800
TORCH_VERSION=${1:-"latest"}

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
  torchlambda --silent build "$TEST_CPP_SOURCE_FOLDER" --destination "$TEST_PACKAGE" --image "$IMAGE"
  unzip -qq "$TEST_PACKAGE" -d "$TEST_CODE"

  # # Create example model
  MODEL="$MODEL" python "$DIR"/src/model.py
  echo "Test $i :: Model size:"
  du -sh "$MODEL"

  SETTINGS="$SETTINGS" OUTPUT="$PAYLOAD" python "$DIR"/src/payload.py
  echo "Test $i :: Payload size:"
  du -sh "$PAYLOAD"

  echo "Test $i :: Setting up server:"
  # container_id=$(docker run --rm -d -e DOCKER_LAMBDA_STAY_OPEN=1 -p 9001:9001 -v \
  #   "$TEST_CODE":/var/task:ro,delegated -v \
  #   "$MODEL":/opt/model.ptc:ro,delegated lambci/lambda:provided \
  #   torchlambda)

  timeout 120 docker run --rm -v \
    "$TEST_CODE":/var/task:ro,delegated -v \
    "$MODEL":/opt/model.ptc:ro,delegated \
    -i -e DOCKER_LAMBDA_USE_STDIN=1 \
    lambci/lambda:provided \
    torchlambda <"$PAYLOAD" >"$RESPONSE"

  echo "Validating received response:"
  SETTINGS="$SETTINGS" RESPONSE="$RESPONSE" python "$DIR"/src/validate.py

  # Clean up
  rm -rf "$SETTINGS" "$TEST_CPP_SOURCE_FOLDER" "$TEST_PACKAGE" "$TEST_CODE" "$MODEL" "$PAYLOAD" "$RESPONSE"
  i=$((i + 1))
done
