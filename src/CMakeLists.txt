cmake_minimum_required(VERSION 3.5...3.16)

if(${CMAKE_VERSION} VERSION_LESS 3.12)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()

project(altorch VERSION 0.1.0
  DESCRIPTION "PyTorch AWS Lambda model inference deployment"
  LANGUAGES CXX
)

# Default to highest available C++ version

set(COMPILATION_OPTIONS "" CACHE STRING "User provided compilation options")

# Set paths to AWS and libtorch

set(AWS_LAMBDA "${CMAKE_CURRENT_SOURCE_DIR}/dependencies/aws-lambda-cpp/build/install")
set(AWS_SDK "${CMAKE_CURRENT_SOURCE_DIR}/dependencies/aws-sdk-cpp/build/install")
set(LIBTORCH "${CMAKE_CURRENT_SOURCE_DIR}/dependencies/pytorch/build_mobile")

set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH};${AWS_LAMBDA};${AWS_SDK};${LIBTORCH}")

# Find torch package

find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

# Find AWS Lambda & SDK packages

find_package(aws-lambda-runtime)
find_package(AWSSDK)

# Add executable

add_executable(${PROJECT_NAME} "main.cpp")

set_target_properties(${PROJECT_NAME} PROPERTIES
  CXX_STANDARD_17
  CXX_STANDARD_REQUIRED YES
  CXX_EXTENSIONS NO
)

include(CheckIPOSupported)
check_ipo_supported(RESULT result)
if(result)
  set_target_properties(${PROJECT_NAME} PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()

target_compile_options(${PROJECT_NAME} PRIVATE ${COMPILATION_OPTIONS})

# Linking and options (--whole-archive is a current workaround)
target_link_libraries(${PROJECT_NAME} PRIVATE -lm
        AWS::aws-lambda-runtime
        ${AWSSDK_LINK_LIBRARIES}
        -Wl,--whole-archive "${TORCH_LIBRARIES}"
        -Wl,--no-whole-archive
        -lpthread
        ${CMAKE_DL_LIBS})


# This line creates a target that packages your binary and zips it up
aws_lambda_package_target(${PROJECT_NAME})
