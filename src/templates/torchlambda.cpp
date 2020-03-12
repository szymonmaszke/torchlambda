#include <string>
#include <vector>

#include <aws/core/Aws.h>
#include <aws/core/utils/memory/stl/AWSString.h>

#include <torch/script.h>

namespace torchlambda {

std::string concatenate(const std::vector<std::string> &fields) {
  std::string result{"["};
  for (const auto &s : fields) {
    result += s;
    result += ", ";
  }
  result += "]";
  return result;
}

bool check_fields(const Aws::Utils::Json::JsonValue &json_view,
                  const std::vector<std::string> &fields) {
  for (const auto &field : fields)
    if (!json_view.ValueExists(Aws::String{field.c_str(), field.size()}))
      return false;

  return true;
}

} // namespace torchlambda
