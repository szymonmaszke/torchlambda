{STATIC}

{GRAD}

{VALIDATE_JSON}

{BASE64}

{VALIDATE_FIELD}

{VALIDATE_SHAPE}

{NORMALIZE}

{CAST}

{DIVIDE}

{RETURN_OUTPUT}

{RETURN_OUTPUT_ITEM}

{RETURN_RESULT}

{RETURN_RESULT_ITEM}

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

#define CREATE_JSON_ARRAY(decoded, data, type, func, ptr_name)                 \
  const auto* ptr_name = data.data_ptr<type>();                          \
  for (int64_t i=0; i < data.numel(); ++i)                                     \
    decoded[i] = Aws::Utils::Json::JsonValue{{}}.func(*ptr_name++);

#define ADD_ITEM(value, func, name, type)                                      \
  func(name, value.flatten().item<type>())


/*!
 *
 *                        REQUEST HANDLER
 *
 */

static aws::lambda_runtime::invocation_response
handler(torch::jit::script::Module &module,
        const aws::lambda_runtime::invocation_request &request
#ifdef BASE64
        , 
        const Aws::Utils::Base64::Base64 &transformer
#endif
  ){{

  const Aws::String data_field{{ {DATA} }};

  /*!
   *
   *               PARSE AND VALIDATE REQUEST
   *
   */

  const auto json = Aws::Utils::Json::JsonValue{{request.payload}};

#ifdef VALIDATE_JSON
  if (!json.WasParseSuccessful())
    return aws::lambda_runtime::invocation_response::failure(
        "Failed to parse request JSON file.", "InvalidJSON");
#endif

  const auto json_view = json.View();

#ifdef VALIDATE_FIELD
  if (!json_view.KeyExists(data_field))
    return aws::lambda_runtime::invocation_response::failure(
        "Required field: \"" {DATA} "\" was not provided.", "InvalidJSON");
#ifdef BASE64
  if (!json_view.GetObject(data_field).IsString())
    return aws::lambda_runtime::invocation_response::failure(
        "Required field: \"" {DATA} "\" is not string.", "InvalidJSON");
#else
  if (!json_view.GetObject(data_field).IsListType())
    return aws::lambda_runtime::invocation_response::failure(
        "Required field: \"" {DATA} "\" is not list type.", "InvalidJSON");
#endif
#endif

#if not defined(STATIC) && defined(VALIDATE_SHAPE)
  /* Check whether all necessary fields are passed */

  const Aws::String fields[]{{ {FIELDS} }};
  for (const auto &field : fields) {{
    if (!json_view.KeyExists(field))
      return aws::lambda_runtime::invocation_response::failure(
          "Required input shape field: '" + std::string{{field.c_str(), field.size()}} +
              "' was not provided.",
          "InvalidJSON");

    if (!json_view.GetObject(field).IsIntegerType())
      return aws::lambda_runtime::invocation_response::failure(
          "Required shape field: '" + std::string{{field.c_str(), field.size()}} +
              "' is not of integer type.",
          "InvalidJSON");
  }}

#endif

  /*!
   *
   *            LOAD DATA, TRANSFORM TO TENSOR, NORMALIZE
   *
   */

#ifdef BASE64
  const auto base64_string = json_view.GetString(data_field);
  const auto data = transformer.Decode(base64_string);
  auto* const data_pointer = data.GetUnderlyingData();
  const std::size_t data_length = data.GetLength();
#else
  const auto nested_json = json_view.GetArray(data_field);
  std::vector<{DATA_TYPE}> data;
  data.reserve(nested_json.GetLength());

  for(size_t i=0; i<nested_json.GetLength(); ++i){{
    data.push_back(static_cast<{DATA_TYPE}>(nested_json[i].{DATA_FUNC}()));
  }}

  auto* const data_pointer = data.data();
  const std::size_t data_length = nested_json.GetLength();
#endif



  /* Const tensor? */
  const torch::Tensor tensor =
#ifdef NORMALIZE
      torch::data::transforms::Normalize<>{{ {{{NORMALIZE_MEANS}}},
                                            {{{NORMALIZE_STDDEVS}}} }}(
#endif
          torch::from_blob(
              data_pointer,
              {{
                  /* Explicit cast as PyTorch has long int for some reason */
                  static_cast<long>(data_length),
              }},
              {TORCH_DATA_TYPE} 
          )
          .reshape( {{{INPUTS}}} )
#ifdef CAST
          .toType( CAST ) 
#endif
#ifdef DIVIDE
          / DIVIDE
#endif
#ifdef NORMALIZE
      )
#endif
      ;

  /*!
   *
   *              MAKE INFERENCE AND RETURN JSON RESPONSE
   *
   */

  /* Support for multi-output/multi-input? */
  const auto output = module.forward({{tensor}}).toTensor()
#ifdef RETURN_OUTPUT
    .toType( {OUTPUT_CAST} )
#endif
  ;


  /* Perform operation to create result */
#if defined(RETURN_RESULT) || defined(RETURN_RESULT_ITEM)
  const auto result = {OPERATIONS_AND_ARGUMENTS};
#endif

  /* If array of outputs to be returned gather values as JSON */
#ifdef RETURN_OUTPUT
  Aws::Utils::Array<Aws::Utils::Json::JsonValue> output_array{{static_cast<std::size_t>(output.numel())}};
  CREATE_JSON_ARRAY(output_array, output, {OUTPUT_TYPE}, {AWS_OUTPUT_FUNCTION}, output_ptr)
#endif

  /* If array of results to be returned gather values as JSON */
#ifdef RETURN_RESULT
  Aws::Utils::Array<Aws::Utils::Json::JsonValue> result_array{{static_cast<std::size_t>(result.numel())}};
  CREATE_JSON_ARRAY(result_array, result, {RESULT_TYPE}, {AWS_RESULT_FUNCTION}, result_ptr)
#endif

  /* Return JSON with response */
  return aws::lambda_runtime::invocation_response::success(
      Aws::Utils::Json::JsonValue{{}}
#ifdef RETURN_RESULT
          .WithArray("{RESULT_NAME}", result_array)
#endif
#ifdef RETURN_RESULT_ITEM
          .ADD_ITEM(result, {AWS_RESULT_ITEM_FUNCTION}, "{RESULT_NAME}", {RESULT_TYPE})
#endif
#ifdef RETURN_OUTPUT
          .WithArray("{OUTPUT_NAME}", output_array)
#endif
#ifdef RETURN_OUTPUT_ITEM
          .ADD_ITEM(output, {AWS_OUTPUT_ITEM_FUNCTION}, "{OUTPUT_NAME}", {OUTPUT_TYPE})
#endif
          .View()
          .WriteCompact(),
      "application/json");
}}

int main() {{

#ifndef GRAD
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
        [&module
#ifdef BASE64
         , &transformer
#endif
        ](const aws::lambda_runtime::invocation_request &request) {{
          return handler(module, request
#ifdef BASE64
              ,transformer
#endif
          );
        }};
    aws::lambda_runtime::run_handler(handler_fn);
  }}
  Aws::ShutdownAPI(options);
  return 0;

}}
