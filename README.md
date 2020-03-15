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

# Comparison with other approaches

# Installation

- [Docker](https://docs.docker.com/) at least of version `17.05` is required.
See [Official Docker's documentation](https://docs.docker.com/) for installation
instruction for your operating system

- Install `torchlambda` through [pip](https://pypi.org/project/pip/), [Python](https://www.python.org/)
version `3.6` or higher is needed. You could also install this software within [conda](https://docs.conda.io/en/latest/)
or other virutal environment of your choice. Following command should be sufficient:
  ```shell
  pip install --user torchlambda
  ```

# Example usage

## 1. Create model to deploy

Below is a code to load `ResNet` from [`torchvision`](https://pytorch.org/docs/stable/torchvision/models.html#classification)
and compile is to [`torchscript`](https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html):

```python
import torch
import torchvision

model = torchvision.models.resnet18()

example = torch.randn(1, 3, 224, 224)
script_model = torch.jit.trace(model, example)

script_model.save("model.ptc")
```

This Python script will create example `model.ptc` in your current working directory.

## 2. Create deployment code with `torchlambda scheme`

Writing C++ code might be hard, hence `torchlambda` provides you
with basic scheme where you can input your problem-specific info.

Issue following command:

```shell
torchlambda scheme
```

You should see a new folder called `torchlambda` in your current directory.
Contents of `torchlambda/main.cpp` are the ones you would usually modify, most of the lines
are heavily commented so it should be easier to follow.

You can see the created C++ code __without comments and guards__ below:

```cpp
/* Here we handle our request */

static aws::lambda_runtime::invocation_response
handler(const aws::lambda_runtime::invocation_request &request,
        torch::jit::script::Module &module,
        const Aws::Utils::Base64::Base64 &transformer) {

  const auto json = Aws::Utils::Json::JsonValue{request.payload};
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

/* Here one should load model, initialize API and create transformer*/

int main(int argc, const char *argv[]) {
  constexpr auto model_path = "/bin/model.ptc";
  torch::jit::script::Module module = torch::jit::load(model_path, torch::kCPU);

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
```

If you are unsure what is going on, please run `torchlambda scheme` and check related
code comments or [post an issue]() if it's still unclear afterwards.


## 3. Package your source with `torchlambda deploy`

Now we have our model and source code. It's time to deploy it as AWS Lambda
ready `.zip` package.

Run from command line:

```shell
torchlambda deploy path/to/torchlambda/folder --compilation "-Wall -O2"
```

Above will create `torchlambda.zip` file ready for deploy.
Notice `--compilation` where you can pass any C++ compilation flags (here `-O2`
for performance optimization).

There are many more things you set during this step, check `torchlambda deploy --help`
for full list of available options.

## 4. Package your model as AWS Lambda Layer

As the above source code is roughly `30Mb` in size (AWS Lambda has `250Mb` limit),
we can put our model as additional layer:

```shell
torchlambda model path/to/model.ptc --destination "resnet.zip"
```

You will receive `resnet.zip` layer in your current working directory.

## 5. Put your model on AWS Lambda!
