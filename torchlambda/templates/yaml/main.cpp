{STATIC}

{CHECK_FIELDS}

{NO_GRAD}

{NORMALIZE}

{RETURN_OUTPUT}

{RETURN_OUTPUT_ITEM}

{RETURN_RESULT}

{RETURN_RESULT_ITEM}

{RESULT_OPERATION_DIM}

#include <string> /* To use for InvalidJson return if any of shape fields not provided */

#include <algorithm>
#include <iterator>

#include <aws/core/Aws.h>
#include <aws/core/utils/base64/Base64.h>
#include <aws/core/utils/json/JsonSerializer.h>
#include <aws/core/utils/memory/stl/AWSString.h>

#include <aws/lambda-runtime/runtime.h>

#include <torch/script.h>
#include <torch/torch.h>

/*!
 *
 *            UTILITY MACROS FOR OUTPUT & RESULT PROCESSING
 *
 */

#define CREATE_JSON_ARRAY(json_array, data, type, func, ptr_name)              \
  auto* ptr_name = data.data_ptr<type>();                                      \
  for (int64_t i=0; i < data.numel(); ++i)                                     \
    json_array[i] = Aws::Utils::Json::JsonValue{{}}.func(std::to_string(i), *ptr_name++);

#define ADD_ITEM(value, func, name, type)                                      \
  func(name, value.flatten().item<type>())


/*!
 *
 *                        REQUEST HANDLER
 *
 */

static aws::lambda_runtime::invocation_response
handler(torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64 &transformer,
        const aws::lambda_runtime::invocation_request &request) {{

  const Aws::String data_field{{ {DATA_FIELD} }};

  /*!
   *
   *               PARSE AND VALIDATE REQUEST
   *
   */

  const auto json = Aws::Utils::Json::JsonValue{{request.payload}};
  if (!json.WasParseSuccessful())
    return aws::lambda_runtime::invocation_response::failure(
        "Failed to parse request JSON file.", "InvalidJSON");

  const auto json_view = json.View();
  if (!json_view.KeyExists(data_field))
    return aws::lambda_runtime::invocation_response::failure(
        "Required field: " {DATA_FIELD} " was not provided.", "InvalidJSON");

#if not defined(STATIC) && defined(CHECK_FIELDS)
  /* Check whether all necessary fields are passed */

  Aws::String fields[]{{ {FIELDS} }};
  for (const auto &field : fields) {{
    if (!json_view.KeyExists(field))
      return aws::lambda_runtime::invocation_response::failure(
          "Required field: " + std::string{{field.c_str(), field.size()}} +
              " was not provided.",
          "InvalidJSON");

    if (!json_view.GetObject(field).IsIntegerType())
      return aws::lambda_runtime::invocation_response::failure(
          "Required field: " + std::string{{field.c_str(), field.size()}} +
              " is not of integer type and cannot act as part of target tensor shape.",
          "InvalidJSON");
  }}

#endif

  /*!
   *
   *            LOAD DATA, TRANSFORM TO TENSOR, NORMALIZE
   *
   */

  const auto base64_data = json_view.GetString(data_field);
  Aws::Utils::ByteBuffer decoded = transformer.Decode(base64_data);

  /* Const tensor? */
  torch::Tensor tensor =
#ifdef NORMALIZE
      torch::data::transforms::Normalize<>{{ {{{NORMALIZE_MEANS}}},
                                            {{{NORMALIZE_STDDEVS}}} }}(
#endif
          torch::from_blob(
              decoded.GetUnderlyingData(),
              {{
                  /* Explicit cast as PyTorch has long int for some reason */
                  static_cast<long>(decoded.GetLength()),
              }},
              torch::TensorOptions().dtype(torch::kUInt8))
              .reshape( {{{INPUT_SHAPE}}} )
              .toType( {CAST} ) /
          {DIVIDE}
#ifdef NORMALIZE
      )
#endif
      ;

  /*!
   *
   *              MAKE INFERENCE AND RETURN JSON RESPONSE
   *
   */

  auto output = module.forward({{tensor}}).toTensor();

  /* Perform operation to create result */
#if defined(RETURN_RESULT) || defined(RETURN_RESULT_ITEM)
  auto result = output.{RESULT_OPERATION}(
#ifdef RESULT_OPERATION_DIM
      RESULT_OPERATION_DIM
#endif
  );
#endif

  /* If array of outputs to be returned gather values as JSON */
#ifdef RETURN_OUTPUT
  Aws::Utils::Array<Aws::Utils::Json::JsonValue> output_array{{}};
  CREATE_JSON_ARRAY(output_array, output, {OUTPUT_TYPE}, {AWS_OUTPUT_FUNCTION}, output_ptr)
#endif

  /* If array of results to be returned gather values as JSON */
#ifdef RETURN_RESULT
  Aws::Utils::Array<Aws::Utils::Json::JsonValue> result_array{{}};
  CREATE_JSON_ARRAY(result_array, result, {RESULT_TYPE}, {AWS_RESULT_FUNCTION}, result_ptr)
#endif

  /* Return JSON with response */
  return aws::lambda_runtime::invocation_response::success(
      Aws::Utils::Json::JsonValue{{}}
#ifdef RETURN_RESULT
          .WithArray("{RESULT_NAME}", result_array)
#endif
#ifdef RETURN_RESULT_ITEM
          .ADD_ITEM(result, {AWS_RESULT_FUNCTION}, {RESULT_NAME}, {RESULT_TYPE})
#endif
#ifdef RETURN_OUTPUT
          .WithArray("{OUTPUT_NAME}", output_array)
#endif
#ifdef RETURN_OUTPUT_ITEM
          .ADD_ITEM(output, {AWS_OUTPUT_FUNCTION}, {OUTPUT_NAME}, {OUTPUT_TYPE})
#endif
          .View()
          .WriteCompact(),
      "application/json");
}}

int main() {{

#ifdef NO_GRAD
  torch::NoGradGuard no_grad_guard{{}};
#endif

  /* Change name/path to your model if you so desire */
  /* Layers are unpacked to /opt, so you are better off keeping it */
  constexpr auto model_path = {MODEL_PATH};

  /* You could add some checks whether the module is loaded correctly */
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
  {{
    const Aws::Utils::Base64::Base64 transformer{{}};
    const auto handler_fn =
        [&module,
         &transformer](const aws::lambda_runtime::invocation_request &request) {{
          return handler(module, transformer, request);
        }};
    aws::lambda_runtime::run_handler(handler_fn);
  }}
  Aws::ShutdownAPI(options);
  return 0;

}}
