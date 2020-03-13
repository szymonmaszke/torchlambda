#include <string>
#include <vector>

#include <aws/core/utils/json/JsonSerializer.h>  // JsonView
#include <aws/core/utils/memory/stl/AWSString.h> // AWS Strings

#include <torch/script.h>

namespace torchlambda {

std::string concatenate(const std::vector<const char *> &fields) {
  std::string result{"["};
  for (const auto &s : fields) {
    result += s;
    result += ", ";
  }
  result += "]";
  return result;
}

bool check_fields(const Aws::Utils::Json::JsonView &json,
                  const std::vector<const char *> &fields) {
  for (const auto &field : fields)
    if (!json.ValueExists(field))
      return false;

  return true;
}

} // namespace torchlambda
