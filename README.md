![torchlambda Logo](https://github.com/szymonmaszke/torchlambda/blob/master/assets/banner.png)

--------------------------------------------------------------------------------

| Version | PyPI | Python | PyTorch | Docker |
|---------|------|--------|---------|--------|
| [![Version](https://img.shields.io/static/v1?label=&message=0.1.1&color=377EF0&style=for-the-badge)](https://github.com/szymonmaszke/torchlambda/releases) | [![Py at least of version `17.05` is required.PI](https://img.shields.io/static/v1?label=&message=PyPI&color=377EF0&style=for-the-badge)](https://pypi.org/project/torchlambda/) | [![Python](https://img.shields.io/static/v1?label=&message=>3.6&color=377EF0&style=for-the-badge&logo=python&logoColor=F8C63D)](https://www.python.org/) | [![PyTorch](https://img.shields.io/static/v1?label=&message=>1.2.0&color=EE4C2C&style=for-the-badge)](https://pytorch.org/) | [![Docker](https://img.shields.io/static/v1?label=&message=>17.05&color=309cef&style=for-the-badge)](https://cloud.docker.com/u/szymonmaszke/repository/docker/szymonmaszke/torchlambda)

[__torchlambda__](https://szymonmaszke.github.io/torchlambda/) is a software designed to deply [PyTorch](https://pytorch.org/) models
on [Amazon's AWS Lambda](https://aws.amazon.com/lambda/) cloud service using [AWS SDK for C++](https://aws.amazon.com/sdk-for-cpp/)
and [custom C++ runtime](https://github.com/awslabs/aws-lambda-cpp).

Using static compilation size of source code is only __`30 Mb` with all necessary dependencies__.
This allows users to pass their models as [AWS Lambda layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html),
hence __no other dependencies like [Amazon S3](https://aws.amazon.com/s3/) are required__.

# Comparison with other deployment tools

__Improve this comparison's reliability via [Pull Request](), thanks.
Also show guys below some love by visiting their projects (just click on the name).__

Trait / Tool | torchlambda | [fastai Lambda](https://course.fast.ai/deployment_aws_lambda.html) | [KubeFlow](https://www.kubeflow.org/) | [Tensorflow Serving](https://github.com/tensorflow/serving) |
|------------|-------------|--------------------------------------------------------------------|------------------|--------------------|
__Autoscaling__ |:heavy_check_mark: | :heavy_check_mark: | with [Kubernetes](https://kubernetes.io/) | with [Kubernetes](https://kubernetes.io/) |
__Light/Heavy load__ | Light  | Light | Heavy/Both | Both |
__GPU Support__ | :x: | :x: | :heavy_check_mark: | :heavy_check_mark: |
__Serverless__ |:heavy_check_mark: | :heavy_check_mark: | :x: | :x: |
__Required services__ | AWS Lambda | AWS Lambda, AWS S3 | Kubernetes Cluster & cloud provider | Deployable in various settings |
__Multiple frameworks__ | :x:  | :x: | :heavy_check_mark: | :x: |
__Latest framework__ <sup>[1](#footnote1)</sup> | :heavy_check_mark: | :x: | :x: | :heavy_check_mark: |
__Version (higher more mature)__ | 0.1.0 | N/A | [1.0](https://github.com/kubeflow/kubeflow/releases/tag/v1.0) | [2.1.0](https://github.com/tensorflow/serving/releases/tag/2.1.0) |
__Customizable dependencies__ <sup>[2](#footnote2)</sup> | :heavy_check_mark: | :x: | :x: | :x: |
__Deployment size__ <sup>[3](#footnote3)</sup>| ~30Mb| +1Gb | N/A | ~67Mb<sup>[4](#footnote4)</sup> |



# Installation

- [Docker](https://docs.docker.com/) at least of version `17.05` is required.
See [Official Docker's documentation](https://docs.docker.com/) for installation
instruction for your operating system

- Install `torchlambda` through [pip](https://pypi.org/project/pip/), [Python](https://www.python.org/)
version `3.6` or higher is needed. You could also install this software within [conda](https://docs.conda.io/en/latest/)
or other virutal environment of your choice. Following command should be sufficient:
  ```shell
  $ pip install --user torchlambda
  ```

# Example deploy

Here is an example of [ResNet18]() model deployment using `torchlambda`.
Run and create all necessary files in the same directory.

## 1. Create model to deploy

Below is a code (`model.py`) to load `ResNet` from [`torchvision`](https://pytorch.org/docs/stable/torchvision/models.html#classification)
and compile is to [`torchscript`](https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html):

```python
import torch
import torchvision

model = torchvision.models.resnet18()

# Smaller example
example = torch.randn(1, 3, 64, 64)
script_model = torch.jit.trace(model, example)

script_model.save("model.ptc")
```

Invoke it from CLI:

```
$ python model.py
```

You should get `model.ptc` in your current working directory.

## 2. Create deployment code with `torchlambda scheme`

Writing C++ code might be hard, hence `torchlambda` provides you
with basic scheme where all you have to do is provide appropriate shapes for inference
(either passed during request or hard-coded).

Issue following command:

```shell
$ torchlambda scheme
```

You should see a new folder called `torchlambda` in your current directory.
Contents of `torchlambda/main.cpp` are the ones you would usually modify.

Only a few usually changes like (e.g. `input shape` or required fields).

If you wish to see the generated C++ scheme code (barely `70` lines) click below:

<details>

  __<summary> Click here to check generated code</summary>__

Code below should be quite easy to follow. Check comments if in doubt or
request improvements in [Issues]() or make a [Pull Request]() if you have an
idea to make this section even easier.

```cpp
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
   *            LOAD DATA, TRANSFORM TO TENSOR, NORMALIZE
   *
   */

  const auto base64_data = json_view.GetString(data_field);
  Aws::Utils::ByteBuffer decoded = transformer.Decode(base64_data);

  /* Copy data and move it to tensor (is there an easier way?) */
  /* Array holds channels * width * height, input your values below */
  float data[3 * 64 * 64];
  std::copy(decoded.GetUnderlyingData(),
            decoded.GetUnderlyingData() + decoded.GetLength() - 1, data);

  torch::Tensor tensor =
      torch::from_blob(data,
                       {
                           static_cast<long int>(decoded.GetLength()),
                       })
          /* Input your data shape for reshape including batch */
          .reshape({1, 3, 64, 64})
          .toType(torch::kFloat32) /
      255.0;

  /* Normalize tensor with ImageNet mean and stddev */
  torch::Tensor normalized_tensor = torch::data::transforms::Normalize<>{
      {0.485, 0.456, 0.406}, {0.229, 0.224, 0.225}}(tensor);

  /*!
   *
   *              MAKE INFERENCE AND RETURN JSON RESPONSE
   *
   */

  /* {} will be casted to std::vector<torch::jit::IValue> under the hood */
  auto output = module.forward({normalized_tensor}).toTensor();
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
  /* Inference doesn't need gradient, let's turn it off */
  torch::NoGradGuard no_grad_guard{};

  /* Change name/path to your model if you so desire */
  /* Layers are unpacked to /opt, so you are better off keeping it */
  constexpr auto model_path = "/opt/model.ptc";

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
```

</details>


## 3. Package your source with torchlambda deploy

Now we have our model and source code. It's time to deploy it as AWS Lambda
ready `.zip` package.

Run from command line:

```shell
$ torchlambda deploy ./torchlambda --compilation "-Wall -O2"
```

Above will create `torchlambda.zip` file ready for deploy.
Notice `--compilation` where you can pass any [C++ compilation flags](https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html) (here `-O2`
for performance optimization).

There are many more things one could set during this step, check `torchlambda deploy --help`
for full list of available options.

Oh, any don't worry about OS compatibility as __this code is compiled on Amazon's AMI Linux__,
if it works here it will work "up there".

## 4. Package your model as AWS Lambda Layer

As the above source code is roughly `30Mb` in size (AWS Lambda has `250Mb` limit),
we can put our model as additional layer. To create it run:

```shell
$ torchlambda model ./model.ptc --destination "model.zip"
```

You will receive `model.zip` layer in your current working directory (`--destination` is optional).

## 5. Deploy to AWS Lambda

From now on you could mostly follow tutorial from [AWS Lambda's C++ Runtime](https://github.com/awslabs/aws-lambda-cpp).
It is assumed you have AWS CLI configured, if not check [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

### 5.1 Create trust policy JSON file

First create the following trust policy JSON file:

```shell
$ cat trust-policy.json
{
 "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": ["lambda.amazonaws.com"]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 5.2 Create IAM role trust policy JSON file

Run from your shell:

```shell
$ aws iam create-role --role-name demo --assume-role-policy-document file://trust-policy.json
```

Note down the role `Arn` returned to you after running that command, it will be needed during next step.

### 5.3 Create AWS Lambda function

Create deployment function with the script below:

```shell
$ aws lambda create-function --function-name demo \
  --role <specify role arn from step 5.2 here> \
  --runtime provided --timeout 30 --memory-size 1024 \
  --handler torchlambda --zip-file fileb://torchlambda.zip
```

### 5.4 Create AWS Layer containing model

We already have our `ResNet18` packed appropriately, run the following:

```shell
$ aws lambda publish-layer-version --layer-name model \
  --description "Resnet18 neural network model" \
  --license-info "MIT" \
  --zip-file fileb://model.zip
```

Please save the `LayerVersionArn` similar to step `5.2` and insert it below to add this layer
to function from step `5.3`:

```shell
$ aws lambda update-function-configuration \
  --function-name demo \
  --layers <specify layer arn from above here>
```

## 6. Encode image with `base64` and request your function

Following script (save it as `request.py`) will send image-like `tensor` encoded using `base64`
via `aws lambda invoke` to test our function.

```python
import base64
import shlex
import struct
import subprocess
import sys

import numpy as np

# Random image-like data
data = np.random.randint(low=0, high=255, size=(3, 64, 64)).flatten().tolist()
# Encode using bytes for AWS Lambda compatibility
image = struct.pack("<{}B".format(len(data)), *data)
encoded = base64.b64encode(image)
command = """aws lambda invoke --function-name %s --payload '{"data":"%s"}' %s""" % (
    sys.argv[1],
    encoded,
    sys.argv[2],
)

subprocess.call(shlex.split(command))
```

Run above script:

```shell
$ python request.py demo output.txt
```

You should get the following response in `output.txt` (your label may vary):

```shell
cat output.txt
  {"label": 40}
```

__Congratulations, you have deployed ResNet18 classifier using only AWS Lambda in 6 steps__!


# Contributing

If you find issue or would like to see some functionality (or implement one), please [open new Issue](https://help.github.com/en/articles/creating-an-issue) or [create Pull Request](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).

#### Footnotes

<a name="footnote1">1</a>. Support for latest version of it's main DL framework or main frameworks if multiple
supported

<a name="footnote2">2</a>. Project dependencies shape can be easily cutomized. In torchlambda case it is customizable
build of [`libtorch`](https://pytorch.org/cppdocs/) and [`AWS C++ SDK`](https://aws.amazon.com/sdk-for-cpp/)

<a name="footnote2">3</a>. Necessary size of code and dependencies to deploy model

<a name="footnote2">4</a>. Based on [Dockerfile size](https://hub.docker.com/r/tensorflow/serving)
