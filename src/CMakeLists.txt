cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

project(tagger LANGUAGES CXX)

# Display current source directory

message(STATUS "Current source directory:")
message(STATUS ${CMAKE_CURRENT_SOURCE_DIR} )

# Set paths to AWS and libtorch

set(AWS_LAMBDA_CPP ${CMAKE_CURRENT_SOURCE_DIR}/dependencies/aws-lambda-cpp/build/install)
set(LIBTORCH ${CMAKE_CURRENT_SOURCE_DIR}/dependencies/pytorch/build_mobile)

set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH};${AWS_LAMBDA_CPP};${LIBTORCH}")

# Find torch package

find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS} -std=c++14")

# Find AWS Lambda package

find_package(aws-lambda-runtime)

# Add executable

add_executable(${PROJECT_NAME} "main.cpp")

# Linking and options
target_link_libraries(${PROJECT_NAME} PUBLIC -lm AWS::aws-lambda-runtime
        -Wl,--whole-archive "${TORCH_LIBRARIES}"
        -Wl,--no-whole-archive
        -lpthread
        ${CMAKE_DL_LIBS})
target_compile_features(${PROJECT_NAME} PUBLIC "cxx_std_14")
target_compile_options(${PROJECT_NAME} PUBLIC "-Wall" "-Wextra" "-O2" "-march=native")

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)

# This line creates a target that packages your binary and zips it up
aws_lambda_package_target(${PROJECT_NAME})
