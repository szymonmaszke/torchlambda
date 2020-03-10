#include <string>
#include <vector>

#include </aws/core/utils/json/JsonSerializer.h>

namespace torchlambda {
std::string concatenate(const std::vector<std::string> &required_fields) {
  std::string result{"["};
  for (auto const &s : required_fields) {
    result += s;
    result += ", ";
  }
  result += "]";
  return result;
}

bool check_fields(const Aws::Utils::Json::JsonValue &json_view,
                  const std::vector<std::string> &required_fields) {
  for (const auto &value : required_fields)
    if (!json_view.ValueExists(value))
      return false;

  return true;
}
} // namespace torchlambda
