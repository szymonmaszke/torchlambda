#include <algorithm>
#include <iterator>

#include <aws/core/Aws.h>
#include <aws/core/utils/base64/Base64.h>
#include <aws/core/utils/json/JsonSerializer.h>
#include <aws/core/utils/memory/stl/AWSString.h>

#include <aws/lambda-runtime/runtime.h>

#include <torch/script.h>
#include <torch/torch.h>

static aws::lambda_runtime::invocation_response
handler(torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64 &transformer,
        const aws::lambda_runtime::invocation_request &request) {

  /* Name of field containing base64 encoded data */
  const Aws::String data_field{"data"};

  /*!
   *
   *               PARSE AND VALIDATE REQUEST
   *        (you may want to add more validations)
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

  /* Create tensor of type Byte from pointer and cast to float32 */
  torch::Tensor tensor =
      torch::from_blob(decoded.GetUnderlyingData(),
                       {
                           static_cast<long>(decoded.GetLength()),
                       },
                       torch::kUInt8)
          /* You may want to pass those values in your request*/
          /* if tensors with dynamic shapes are provided */
          .reshape({1, 3, 64, 64})
          .toType(torch::kFloat32) /
      255.0;

  /* Normalize tensor with ImageNet means and standard deviations */
  torch::Tensor normalized_tensor = torch::data::transforms::Normalize<>{
      {0.485, 0.456, 0.406}, {0.229, 0.224, 0.225}}(tensor);

  /*!
   *
   *              MAKE INFERENCE AND RETURN JSON RESPONSE
   *
   */

  /* {} will be casted to std::vector<torch::jit::IValue> under the hood */
  auto output = module.forward({normalized_tensor}).toTensor();
  /* As only single element will be outputted from argmax we can use item */
  const int label = torch::argmax(output).item<int>();

  /* Return JSON with field label containing predictions*/
  return aws::lambda_runtime::invocation_response::success(
      Aws::Utils::Json::JsonValue{}
          .WithInteger("label", label)
          .View()
          .WriteCompact(),
      "application/json");
}

int main() {
  /* Inference doesn't usually need gradient, let's turn it off */
  torch::NoGradGuard no_grad_guard{};

  /* Layers are unpacked to /opt if you are passing your model this way */
  constexpr auto model_path = "/opt/model.ptc";

  /* You could add some checks whether the module is loaded correctly */
  /* Module should be loaded here for faster inference and shared via context */
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
