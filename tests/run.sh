#!/usr/bin/env sh

set -e

# Global test run settings

TORCH_VERSION=$1

IMAGE="szymonmaszke/torchlambda:$TORCH_VERSION"

SETTINGS="settings.yaml"
TEST_SETTINGS="test_settings.yaml"

TEST_CPP_SOURCE_FOLDER="test_cpp_source_folder"
TEST_PACKAGE="deployment.zip"
TEST_CODE="test_code"
MODEL="model.ptc"
OUTPUT="output.json"

EVENT_FILE="request.json"

# Run for each test case

for test_case in tests/cases/*.json; do
  printf "\nTEST: %s\n\n" "$test_case"

  # Get default settings
  echo "$test_case: Creating general settings"
  torchlambda settings --destination "$SETTINGS"

  # Insert test case specific values into settings
  echo "$test_case: Setup test settings"
  SETTINGS="$SETTINGS" OUTPUT="$TEST_SETTINGS" python tests/src/setup_test.py "$test_case"

  # Use test settings to create C++ code template
  echo "$test_case: Creating source code from settings"
  torchlambda template --yaml "$TEST_SETTINGS" --destination "$TEST_CPP_SOURCE_FOLDER"

  # Build code template into deployment package
  echo "$test_case: Building source code"
  torchlambda build "$TEST_CPP_SOURCE_FOLDER" --destination "$TEST_PACKAGE" --image "$IMAGE"
  unzip -qq "$TEST_PACKAGE" -d "$TEST_CODE"

  # Create example model
  echo "$test_case: Creating specified model"
  MODEL="$MODEL" python tests/src/model.py "$test_case"

  # Do not pack layer (lambci needs unpacked code and layers)
  echo "$test_case: Request output from function"
  OUTPUT_FILE=$OUTPUT EVENT_FILE="$EVENT_FILE" OUTPUT="$OUTPUT" TEST_CODE="$TEST_CODE" MODEL="$MODEL" timeout 40 python tests/src/request.py "$test_case"
  echo "Size of request:"
  du -sh $EVENT_FILE

  # Clean up
  rm -rf $SETTINGS $TEST_SETTINGS $TEST_CPP_SOURCE_FOLDER $TEST_PACKAGE $TEST_CODE $MODEL $EVENT_FILE
done
