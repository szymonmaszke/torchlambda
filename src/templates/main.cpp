#include <iostream>
#include <memory>
#include <string>

#include </aws/core/utils/json/JsonSerializer.h>
#include <aws/core/Aws.h>
#include <aws/core/utils/HashingUtils.h>

#include <aws/lambda-runtime/runtime.h>

#include <torch/script.h>

std::string concatenate(const std::vector<std::string> &needed_values) {
  std::string result{"["};
  for (auto const &s : needed_values) {
    result += s;
    result += ", ";
  }
  result += "]";
  return result;
}

bool values_exist(const Aws::Utils::Json::JsonValue &json_view,
                  const std::vector<std::string> &needed_values) {
  for (const auto &value : needed_values)
    if (!json_view.ValueExists(value))
      return false;

  return true;
}

static aws::lambda_runtime::invocation_response
handler(const aws::lambda_runtime::invocation_request &request,
        const torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64::Base64 &transformer) {

  auto json = Aws::Utils::Json::JsonValue{request.payload};
  if (!json.WasParseSuccessful())
    return aws::lambda_runtime::invocation_response::failure(
        "Failed to parse input JSON file.", "InvalidJSON");

  if (!values_exist(json_view, needed_values))
    return aws::lambda_runtime::invocation_response::failure(
        "One or more of needed values: " + concatenate(needed_values) +
            " wasn't passed in request.",
        "InvalidJSON");

  auto json_view = json.View();

  // Repeat below until all required data is checked to exist
  // In this case image is required key in passed JSON to Lambda
  // Also image shape is required (e.g. channels, height, width)
  const auto base64_data = json_view.GetString("image");
  if (!base64_data.IsString())
    return aws::lambda_runtime::invocation_response::failure(
        "Image should be base64 encoded string.", "InvalidJSON");

  const auto tensor =
      torch::from_blob(transformer.Decode(base64_data).GetUnderlyingData(),
                       at::IntList({1, channels, width, height}))
          .toType(at::kFloat) /
      255.;

  auto result = module.forward({tensor}).toTensor().data<float>();

  auto output = ::Base64Encode(bb);
  return aws::lambda_runtime::invocation_response::success(request.payload,
                                                           "application/json");
}

int main(int argc, const char *argv[]) {
  // Use AWS-Shared-ptr or some shit
  torch::jit::script::Module module = torch::jit::load("/bin/model.ptc");

  Aws::SDKOptions options;
  Aws::InitAPI(options);
  {
    // Use AWS-Shared-ptr as well?
    const Aws::Utils::Base64::Base64::Base64 transformer{};
    auto handler_fn =
        [&module,
         &transformer](const aws::lambda_runtime::invocation_request &request) {
          return handler(req, module, transformer);
        };

    aws::lambda_runtime::run_handler(handler_fn);
  }
  Aws::ShutdownAPI(options);

  return 0;
}
