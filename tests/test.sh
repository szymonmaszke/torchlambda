#!/usr/bin/env sh

IMAGE="torchlambda:custom"

SETTINGS="./settings.yaml"
TEST_SETTINGS="./test_settings.yaml"
TEST_CPP_SOURCE_FOLDER="./test_cpp_source_folder"
TEST_PACKAGE="./deployment.zip"
TEST_CODE="./test_code"
OUTPUT="./output.json"

for test_filename in tests/cases/*.json; do
  # Create test case
  torchlambda settings --destination "$SETTINGS"
  python3 tests/src/setup_test.py "$SETTINGS" "$test_filename" "$TEST_SETTINGS"

  # Create C++ source code
  torchlambda template --yaml "$TEST_SETTINGS" --destination "$TEST_CPP_SOURCE_FOLDER"

  # Setup
  torchlambda build "$TEST_CPP_SOURCE_FOLDER" --destination "$TEST_PACKAGE" --image "$IMAGE"
  unzip "$TEST_PACKAGE" -d "$TEST_CODE"

  OUTPUT="$OUTPUT" TEST_CODE="$TEST_CODE" MODEL="$MODEL" python3 tests/src/request.py "$TEST_SETTINGS" | jq -r '.STATUS_CODE '
  if [ $OUTPUT != 200 ]; then
    echo "Test:: Wrong output code from AWS Lambda inference for: $test_filename"
    exit 1
  fi

  # Clean up
  rm -rf $SETTINGS $TEST_SETTINGS $TEST_CPP_SOURCE_FOLDER $TEST_PACKAGE $TEST_CODE $OUTPUT
done
