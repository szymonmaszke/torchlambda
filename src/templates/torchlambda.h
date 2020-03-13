#pragma once

#include <string>
#include <vector>

#include <aws/core/Aws.h>
#include <aws/core/utils/base64/Base64.h>       // Base64
#include <aws/core/utils/json/JsonSerializer.h> // JSON
#include <aws/core/utils/memory/stl/AWSString.h>

#include <torch/script.h>

namespace torchlambda {
namespace utils {

inline int get(const Aws::Utils::Json::JsonView &json,
               const std::string &field) {
  return json.GetInteger(field);
}

inline int get(const Aws::Utils::Json::JsonView &json, int number) {
  return number;
}

} // namespace utils

template <typename... Args>
auto base64_to_tensor(const Aws::Utils::Base64::Base64 &transformer,
                      const Aws::String &data,
                      const Aws::Utils::Json::JsonView &json, Args... args) {
  return torch::from_blob(transformer.Decode(data).GetUnderlyingData(),
                          at::IntList({utils::get(json, args)...}));
}

std::string concatenate(const std::vector<const char *> &fields);

bool check_fields(const Aws::Utils::Json::JsonView &json_view,
                  const std::vector<const char *> &fields);

} // namespace torchlambda
