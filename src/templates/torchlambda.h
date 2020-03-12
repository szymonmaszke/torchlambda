#pragma once

#include <string>
#include <vector>

#include <aws/core/Aws.h>
#include <aws/core/utils/json/JsonSerializer.h>
#include <aws/core/utils/memory/stl/AWSString.h>

#include <torch/script.h>

namespace torchlambda {
namespace utils {

inline int get(const Aws::Utils::Json::JsonView &view,
               const std::string &field) {
  return view.GetInteger(field);
}

inline int get(const Aws::Utils::Json::JsonView &view, int number) {
  return number;
}

} // namespace utils

template <typename... Args>
auto base64_to_tensor(const Aws::Utils::Base64::Base64 &transformer,
                      const Aws::String &data,
                      const Aws::Utils::Json::JsonView &view, Args... args) {
  return torch::from_blob(transformer.Decode(data).GetUnderlyingData(),
                          at::IntList({utils::get(view, args)...}));
}

std::string concatenate(const std::vector<std::string> &fields);

bool check_fields(const Aws::Utils::Json::JsonValue &json_view,
                  const std::vector<std::string> &fields);

} // namespace torchlambda
