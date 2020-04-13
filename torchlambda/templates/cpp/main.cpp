#include <aws/core/Aws.h>
#include <aws/core/utils/base64/Base64.h>
#include <aws/core/utils/json/JsonSerializer.h>
#include <aws/core/utils/memory/stl/AWSString.h>

#include <aws/lambda-runtime/runtime.h>

#include <torch/script.h>
#include <torch/torch.h>

/*!
 *
 *                    HANDLE REQUEST
 *
 */

static aws::lambda_runtime::invocation_response
handler(torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64 &transformer,
        const aws::lambda_runtime::invocation_request &request) {

  const Aws::String data_field{"data"};

  /*!
   *
   *              PARSE AND VALIDATE REQUEST
   *
   */

  const auto json = Aws::Utils::Json::JsonValue{request.payload};
  if (!json.WasParseSuccessful())
    return aws::lambda_runtime::invocation_response::failure(
        "Failed to parse input JSON file.", "InvalidJSON");

  const auto json_view = json.View();
  if (!json_view.KeyExists(data_field))
    return aws::lambda_runtime::invocation_response::failure(
        "Required data was not provided.", "InvalidJSON");

  /*!
   *
   *          LOAD DATA, TRANSFORM TO TENSOR, NORMALIZE
   *
   */

  const auto base64_data = json_view.GetString(data_field);
  Aws::Utils::ByteBuffer decoded = transformer.Decode(base64_data);

  torch::Tensor tensor =
      torch::from_blob(decoded.GetUnderlyingData(),
                       {
                           static_cast<long>(decoded.GetLength()),
                       },
                       torch::kUInt8)
          .reshape({1, 3, 64, 64})
          .toType(torch::kFloat32) /
      255.0;

  torch::Tensor normalized_tensor = torch::data::transforms::Normalize<>{
      {0.485, 0.456, 0.406}, {0.229, 0.224, 0.225}}(tensor);

  /*!
   *
   *                      MAKE INFERENCE
   *
   */

  auto output = module.forward({normalized_tensor}).toTensor();
  const int label = torch::argmax(output).item<int>();

  /*!
   *
   *                       RETURN JSON
   *
   */

  return aws::lambda_runtime::invocation_response::success(
      Aws::Utils::Json::JsonValue{}
          .WithInteger("label", label)
          .View()
          .WriteCompact(),
      "application/json");
}

int main() {
  /*!
   *
   *                        LOAD MODEL ON CPU
   *                    & SET IT TO EVALUATION MODE
   *
   */

  /* Turn off gradient */
  torch::NoGradGuard no_grad_guard{};
  /* No optimization during first pass as it might slow down inference by 30s */
  torch::jit::setGraphExecutorOptimize(false);

  constexpr auto model_path = "/opt/model.ptc";

  torch::jit::script::Module module = torch::jit::load(model_path, torch::kCPU);
  module.eval();

  /*!
   *
   *                        INITIALIZE AWS SDK
   *                    & REGISTER REQUEST HANDLER
   *
   */

  Aws::SDKOptions options;
  Aws::InitAPI(options);
  {
    const Aws::Utils::Base64::Base64 transformer{};
    const auto handler_fn =
        [&module,
         &transformer](const aws::lambda_runtime::invocation_request &request) {
          return handler(module, transformer, request);
        };
    aws::lambda_runtime::run_handler(handler_fn);
  }
  Aws::ShutdownAPI(options);
  return 0;
}
