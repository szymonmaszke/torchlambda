#include <iostream>
#include <memory>
#include <string>

#include <aws/core/Aws.h>
#include <aws/core/utils/HashingUtils.h>
#include <aws/core/utils/json/JsonSerializer.h>

#include <aws/lambda-runtime/runtime.h>

#include <torch/script.h>

#include "torchlambda.h"

static aws::lambda_runtime::invocation_response
handler(const aws::lambda_runtime::invocation_request &request,
        const torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64 &transformer) {

  /*!
   *
   *                 CASE SPECIFIC VALUES
   *             CHANGE WHAT YOU NEED BELOW
   *
   */

  /* Name of field containing tensor data encoded via base64 */
  constexpr auto data_field = "image";

  /* Define needed fields in request */
  /* data_field is provided as well as it will be checked with other fields */
  /* Here channels, width and height are needed for tensor reshape below*/
  const std::vector<const std::string> required_fields{data_field, "channels",
                                                       "width", "height"};

  /* Size of neural network output */
  /* Can be 1 for binary classification or 10 for multiclass */
  constexpr std::size_t output_size = 100;

  /*!
   *
   *                 ARGUMENT PARSING
   *             AND ASSERTIONS VALIDATION
   *
   */

  const auto json = Aws::Utils::Json::JsonValue{request.payload};
  if (!json.WasParseSuccessful())
    return aws::lambda_runtime::invocation_response::failure(
        "Failed to parse input JSON file.", "InvalidJSON");

  const auto json_view = json.View();

  if (!torchlambda::check_fields(json_view, required_fields))
    return aws::lambda_runtime::invocation_response::failure(
        "One or more of needed fields: " +
            torchlambda::concatenate(required_fields) +
            " were not provided in request.",
        "InvalidJSON");

  /*!
   *
   *                 OBTAINING DATA
   *             AND ASSERTIONS VALIDATION
   *
   */

  /* Get data from JSON view and check whether it is string */
  const auto base64_data = json_view.GetString(data_field);
  if (!base64_data.IsString())
    return aws::lambda_runtime::invocation_response::failure(
        "Data should be base64 encoded string.", "InvalidJSON");

  /* Create tensor from base64 encoded data passed in request */
  const auto tensor = torchlambda::base64_to_tensor(
      transformer, base64_data, json_view,
      /* Pass desired shape of tensor below */
      /* Either ints or names of fields supported */
      1, "channels", "width", "height");

  /* Byte tensors are returned hence those should be usually casted to Float */
  auto output = module.forward({tensor.toType(at::kFloat) / 255.}).toTensor();
  /* Booleans for 0-1 classification, change type appropriately */
  const bool *result_array = (output > 0.5).data<bool>();

  return aws::lambda_runtime::invocation_response::success(
      transformer.Encode(result_array, output_size); "application/json");
}

int main(int argc, const char *argv[]) {
  /*!
   *
   *                          MODEL LOADING
   *
   */
  /* Define path to trained model, usually in /bin/model.ptc as specified */
  constexpr auto model_path = "/bin/model.ptc";
  // Use AWS-Shared-ptr or some shit
  torch::jit::script::Module module = torch::jit::load("/bin/model.ptc");

  Aws::SDKOptions options;
  Aws::InitAPI(options);
  {
    // Base64 transformer of input data
    const Aws::Utils::Base64::Base64 transformer{};
    auto handler_fn =
        [&module,
         &transformer](const aws::lambda_runtime::invocation_request &request) {
          return handler(request, module, transformer);
        };

    aws::lambda_runtime::run_handler(handler_fn);
  }
  Aws::ShutdownAPI(options);

  return 0;
}
