#include <aws/core/Aws.h>
#include <aws/core/utils/base64/Base64.h>
#include <aws/core/utils/json/JsonSerializer.h>
#include <aws/core/utils/memory/stl/AWSString.h>

#include <aws/lambda-runtime/runtime.h>

#include <torch/script.h>
#include <torch/torch.h>

static aws::lambda_runtime::invocation_response
handler(const aws::lambda_runtime::invocation_request &request,
        torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64 &transformer) {

  /* Name of field containing base64 encoded data */
  const Aws::String data_field{"data"};

  /*!
   *
   *               PARSE AND VALIDATE REQUEST
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
   *            LOAD DATA AND TRANSFORM TO TENSOR
   *
   */

  /* Get data from JSON view and check whether it is string */
  const auto base64_data = json_view.GetString(data_field);

  /* Create Byte tensor from base64 encoded data passed in request */
  const auto tensor =
      torch::from_blob(transformer.Decode(base64_data).GetUnderlyingData(),
                       /* Shape of tensor, [batch, channels, width, height] */
                       torch::IntList({1, 3, 224, 224}));

  /* Normalize Tensor using ImageNet mean and stddev */
  auto output = module
                    .forward({torch::data::transforms::Normalize<>{
                        {0.485, 0.456, 0.406}, {0.229, 0.224, 0.225}}(
                        tensor.toType(torch::kFloat32) / 255.)})
                    .toTensor();

  /* Get label using argmax */
  const int label = torch::argmax(output).item<int>();

  /* Return statusCode and found label */
  return aws::lambda_runtime::invocation_response::success(
      Aws::Utils::Json::JsonValue{}
          .WithInteger("statusCode", 200)
          .WithInteger("label", label)
          .View()
          .WriteCompact(),
      "application/json");
}

int main(int argc, const char *argv[]) {
  /*!
   *
   *                          PYTORCH MODEL
   *
   */
  /* Disable gradient as it's not needed for inference */
  torch::NoGradGuard no_grad_guard{};

  /* Define path to trained model, usually in /bin/model.ptc as specified */
  constexpr auto model_path = "/bin/model.ptc";
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
    // Base64 transformer of input data
    const Aws::Utils::Base64::Base64 transformer{};
    const auto handler_fn =
        [&module,
         &transformer](const aws::lambda_runtime::invocation_request &request) {
          return handler(request, module, transformer);
        };

    aws::lambda_runtime::run_handler(handler_fn);
  }
  Aws::ShutdownAPI(options);

  return 0;
}
