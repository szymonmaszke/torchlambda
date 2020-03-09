![torchlambda Logo](https://github.com/szymonmaszke/torchlambda/blob/master/assets/banner.png)

--------------------------------------------------------------------------------

| Version | Docs | Tests | Coverage | Style | PyPI | Python | PyTorch | Docker | Roadmap |
|---------|------|-------|----------|-------|------|--------|---------|--------|---------|
| [![Version](https://img.shields.io/static/v1?label=&message=0.1.1&color=377EF0&style=for-the-badge)](https://github.com/szymonmaszke/torchlambda/releases) | [![Documentation](https://img.shields.io/static/v1?label=&message=docs&color=EE4C2C&style=for-the-badge)](https://szymonmaszke.github.io/torchlambda/)  | ![Tests](https://github.com/szymonmaszke/torchlambda/workflows/test/badge.svg) | ![Coverage](https://img.shields.io/codecov/c/github/szymonmaszke/torchlambda?label=%20&logo=codecov&style=for-the-badge) | [![codebeat](https://img.shields.io/static/v1?label=&message=CB&color=27A8E0&style=for-the-badge)](https://codebeat.co/projects/github-com-szymonmaszke-torchlambda-master) | [![PyPI](https://img.shields.io/static/v1?label=&message=PyPI&color=377EF0&style=for-the-badge)](https://pypi.org/project/torchlambda/) | [![Python](https://img.shields.io/static/v1?label=&message=3.7&color=377EF0&style=for-the-badge&logo=python&logoColor=F8C63D)](https://www.python.org/) | [![PyTorch](https://img.shields.io/static/v1?label=&message=1.2.0&color=EE4C2C&style=for-the-badge)](https://pytorch.org/) | [![Docker](https://img.shields.io/static/v1?label=&message=docker&color=309cef&style=for-the-badge)](https://cloud.docker.com/u/szymonmaszke/repository/docker/szymonmaszke/torchlambda) | [![Roadmap](https://img.shields.io/static/v1?label=&message=roadmap&color=009688&style=for-the-badge)](https://github.com/szymonmaszke/torchlambda/blob/master/ROADMAP.md) |

[__torchlambda__](https://szymonmaszke.github.io/torchlambda/) is  [PyTorch](https://pytorch.org/) model deployment
script for [Amazon's AWS Lambda](https://aws.amazon.com/lambda/) cloud service using [AWS SDK for C++](https://aws.amazon.com/sdk-for-cpp/)
and [custom C++ runtime](https://github.com/awslabs/aws-lambda-cpp).

Using static compilation deployment code is usually around __only `50 Mb` of size (maybe even less)__ which
allows the user to pass models (of up to `200 Mb`) as Lambda layers.

No [`S3`](https://aws.amazon.com/s3/), no other dependencies, just PyTorch and AWS Lambda.
