cmake_minimum_required(VERSION 3.5...3.16)

if(${CMAKE_VERSION} VERSION_LESS 3.12)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()

project(torchlambda VERSION 0.1.0
  DESCRIPTION "PyTorch AWS Lambda model inference deployment"
  LANGUAGES CXX
)

set(AWS_COMPONENTS "core" CACHE STRING "AWS-SDK Components used by user")

# All dependencies are in /usr/local already

# Find torch package
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

# Find AWS Lambda
find_package(aws-lambda-runtime REQUIRED)

# AWS_COMPONENTS is already set during image build
find_package(AWSSDK REQUIRED COMPONENTS ${AWS_COMPONENTS})

# Add all C/C++ files
file(GLOB_RECURSE DEPLOYMENT_SRC
    "${CMAKE_CURRENT_SOURCE_DIR}/user_code/*.hpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/user_code/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/user_code/*.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/user_code/*.c"
)

add_executable(${PROJECT_NAME} ${DEPLOYMENT_SRC})

set_target_properties(${PROJECT_NAME} PROPERTIES
  CXX_STANDARD 17
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
