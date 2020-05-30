<img align="left" width="256" height="256" src="https://github.com/szymonmaszke/torchlambda/blob/master/assets/banner.png">

[__torchlambda__](https://github.com/szymonmaszke/torchlambda/wiki) is a tool to deploy [PyTorch](https://pytorch.org/) models
on [Amazon's AWS Lambda](https://aws.amazon.com/lambda/) using [AWS SDK for C++](https://aws.amazon.com/sdk-for-cpp/)
and [custom C++ runtime](https://github.com/awslabs/aws-lambda-cpp).

Using statically compiled dependencies __whole package is shrunk to only `30MB`__.

Due to small size of compiled source code users can pass their models as [AWS Lambda layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).
__Services like [Amazon S3](https://aws.amazon.com/s3/) are no longer necessary to load your model__.

[__torchlambda__](https://github.com/szymonmaszke/torchlambda/wiki) has it's PyTorch & AWS dependencies always tested & up to date because of [continuous deployment](https://en.wikipedia.org/wiki/Continuous_deployment) run at `03:00 a.m.`
every day.


| Docs | Deployment | Package | Python | PyTorch | Docker | CodeBeat | Images |
|------|------------|---------|--------|---------|--------|----------|--------|
|[![Documentation](https://img.shields.io/static/v1?label=&message=Wiki&color=EE4C2C&style=for-the-badge)](https://github.com/szymonmaszke/torchlambda/wiki) | ![CD](https://img.shields.io/github/workflow/status/szymonmaszke/torchlambda/update?label=%20&style=for-the-badge) | [![PyPI](https://img.shields.io/static/v1?label=&message=PyPI&color=377EF0&style=for-the-badge)](https://pypi.org/project/torchlambda/) | [![Python](https://img.shields.io/static/v1?label=&message=3.6&color=377EF0&style=for-the-badge&logo=python&logoColor=F8C63D)](https://www.python.org/) | [![PyTorch](https://img.shields.io/static/v1?label=&message=1.4.0&color=EE4C2C&style=for-the-badge)](https://pytorch.org/) | [![Docker](https://img.shields.io/static/v1?label=&message=17.05&color=309cef&style=for-the-badge)](https://cloud.docker.com/u/szymonmaszke/repository/docker/szymonmaszke/torchlambda) | [![codebeat badge](https://codebeat.co/badges/ca6f19c8-29ad-4ddb-beb3-4d4e2fb3aba2)](https://codebeat.co/projects/github-com-szymonmaszke-torchlambda-master) | [![Images](https://img.shields.io/static/v1?label=&message=Tags&color=309cef&style=for-the-badge)](https://hub.docker.com/r/szymonmaszke/torchlambda/tags)|


# Why should I use `torchlambda`?

- __Lightweight & latest dependencies__ - compiled source code weights only `30MB`. Previous approach to PyTorch network deployment on AWS Lambda ([fastai](https://course.fast.ai/deployment_aws_lambda.html)) uses outdated PyTorch (`1.1.0`) as dependency layer and requires AWS S3 to host your model. Now you can only use AWS Lambda and host your model as layer.
- __Cheaper and less resource hungry__ - available solutions run server hosting incoming requests all the time. AWS Lambda (and torchlambda) runs only when the request comes. 
- __Easy automated scaling__  usually autoscaling is done with [Kubernetes](https://kubernetes.io/) or similar tools (see [KubeFlow](https://www.kubeflow.org/docs/gke/deploy/)). This approach requires knowledge of another tool, setting up appropriate services (e.g. [Amazon EKS](https://aws.amazon.com/eks/)). In AWS Lambda case you just push your neural network inference code and you are done.
- __Easy to use__ - no need to learn new tool. `torchlambda` has at most
`4` commands and deployment is done via [YAML](https://yaml.org/) settings. No need to modify your PyTorch code.
- __Do one thing and do it well__ - most deployment tools are complex solutions
including multiple frameworks and multiple services. `torchlambda` focuses
solely on inference of PyTorch models on AWS Lambda.
- __Write programs to work together__ - This tool does not repeat PyTorch & AWS's functionalities (like `aws-cli`). You can also use your favorite third party tools (say [saws](https://github.com/donnemartin/saws), [Terraform](https://www.terraform.io/) with AWS and [MLFlow](https://www.mlflow.org/docs/latest/index.html), [PyTorch-Lightning](https://github.com/PyTorchLightning/pytorch-lightning) to train your model).
- __Test locally, run in the cloud__ - `torchlambda` uses [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2/) Docker [images](https://hub.docker.com/_/amazonlinux) under the hood & allows you to use [lambci/docker-lambda](https://github.com/lambci/docker-lambda) to test your deployment on `localhost` before pushing deployment to the cloud (see [Test Lambda deployment locally](https://github.com/szymonmaszke/torchlambda/wiki/Test-Lambda-deployment-locally) tutorial).
- __Extensible when you need it__ - All you usually need are a few lines of YAML settings, but if you wish to fine-tune your deployment you can use `torchlambda build` `--flags` (changing various properties of PyTorch and AWS dependencies themselves). You can also write your own C++ deployment code (generate template via `torchlambda template` command).
- __Small is beautiful__ - `3000` LOC (most being convenience wrapper creating this tool)
make it easy to jump into source code and check what's going on under the hood.


# Table Of Contents

- [Installation](https://github.com/szymonmaszke/torchlambda/wiki/Installation)
- [Tutorials](https://github.com/szymonmaszke/torchlambda/wiki/Tutorials)
	- [ResNet18 deployment on AWS Lambda](https://github.com/szymonmaszke/torchlambda/wiki/ResNet18-deployment-on-AWS-Lambda)
	- [Test Lambda deployment locally](https://github.com/szymonmaszke/torchlambda/wiki/Test-Lambda-deployment-locally)
	- [`base64` image encoding](https://github.com/szymonmaszke/torchlambda/wiki/base64-image-encoding)
- [Commands](https://github.com/szymonmaszke/torchlambda/wiki/Commands)
	- [settings](https://github.com/szymonmaszke/torchlambda/wiki/Commands#torchlambda-settings)
	- [template](https://github.com/szymonmaszke/torchlambda/wiki/Commands#torchlambda-template)
	- [build](https://github.com/szymonmaszke/torchlambda/wiki/Commands#torchlambda-build)
	- [layer](https://github.com/szymonmaszke/torchlambda/wiki/Commands#torchlambda-layer)
- [YAML settings file reference](https://github.com/szymonmaszke/torchlambda/wiki/YAML-settings-file-reference)
- [C++ code](https://github.com/szymonmaszke/torchlambda/wiki/CPP---code)
