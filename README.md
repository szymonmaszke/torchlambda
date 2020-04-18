<img align="left" width="256" height="256" src="https://github.com/szymonmaszke/torchlambda/blob/master/assets/banner.png">

[__torchlambda__](https://szymonmaszke.github.io/torchlambda/) is a tool to deploy [PyTorch](https://pytorch.org/) models
on [Amazon's AWS Lambda](https://aws.amazon.com/lambda/) using [AWS SDK for C++](https://aws.amazon.com/sdk-for-cpp/)
and [custom C++ runtime](https://github.com/awslabs/aws-lambda-cpp).

Using statically compiled dependencies __whole package is shrunk to only `30MB`__.

Due to small size of compiled source code users can pass their models as [AWS Lambda layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).
__Services like [Amazon S3](https://aws.amazon.com/s3/) are no longer necessary to load your model__.

[__torchlambda__](https://szymonmaszke.github.io/torchlambda/) has it's PyTorch & AWS dependencies always up to date because of [continuous deployment](https://en.wikipedia.org/wiki/Continuous_deployment) run at `03:00 a.m.`
every day.


| Docs | Deployment | Package | Python | PyTorch | Docker | CodeBeat | Images |
|------|------------|---------|--------|---------|--------|----------|--------|
|[![Documentation](https://img.shields.io/static/v1?label=&message=Wiki&color=EE4C2C&style=for-the-badge)](https://github.com/szymonmaszke/torchlambda/wiki) | ![CD](https://img.shields.io/github/workflow/status/szymonmaszke/torchlambda/update?label=%20&style=for-the-badge) | [![PyPI](https://img.shields.io/static/v1?label=&message=PyPI&color=377EF0&style=for-the-badge)](https://pypi.org/project/torchlambda/) | [![Python](https://img.shields.io/static/v1?label=&message=3.6&color=377EF0&style=for-the-badge&logo=python&logoColor=F8C63D)](https://www.python.org/) | [![PyTorch](https://img.shields.io/static/v1?label=&message=1.4.0&color=EE4C2C&style=for-the-badge)](https://pytorch.org/) | [![Docker](https://img.shields.io/static/v1?label=&message=17.05&color=309cef&style=for-the-badge)](https://cloud.docker.com/u/szymonmaszke/repository/docker/szymonmaszke/torchlambda) | [![codebeat badge](https://codebeat.co/badges/ca6f19c8-29ad-4ddb-beb3-4d4e2fb3aba2)](https://codebeat.co/projects/github-com-szymonmaszke-torchlambda-master) | [![Images](https://img.shields.io/static/v1?label=&message=Tags&color=309cef&style=for-the-badge)](https://hub.docker.com/r/szymonmaszke/torchlambda/tags)|


# Comparison with other deployment tools

- __Do one thing and do it well__ - most deployment tools are complex solutions
including multiple frameworks and multiple services. `torchlambda` focuses
solely on PyTorch and AWS Lambda integration.
- __Write programs to work together__ - Amazon AWS & PyTorch exist for a reason,
no need to repeat their functionalities (like `aws-cli`). No source code modifications
of your neural networks required either.
- __Small is beautiful__ - `3000` LOC (most being convenience wrapper creating this tool)
make it easy to delve into source code and modify what you want on your own.
- __Integration with other tools__ - as `torchlambda` focuses on narrow space you can
use any tools you like with PyTorch (e.g. for training you can use [KubeFlow](https://github.com/kubeflow/kubeflow) or [BentoML](https://github.com/bentoml/BentoML)) and AWS (for example [Terraform](https://www.terraform.io/)).
- __Easy to jump in__ - no need to learn new tool. `torchlambda` has at most
`4` commands simplifying steps to take PyTorch model into the cloud which are mostly repetitive and possible
to automate further.
- __Extensible when you need it__ - All you usually need are a few lines of YAML settings, but if you wish to fine-tune your deployment you can use `torchlambda build` `--flags` (changing various properties of PyTorch and AWS dependencies).


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

#### Footnotes

<a name="footnote1">1</a>. Support for latest version of it's main DL framework or main frameworks if multiple
supported

<a name="footnote2">2</a>. Project dependencies are easily customizable. In torchlambda it would be user
specified build procedures for [`libtorch`](https://pytorch.org/cppdocs/) and [`AWS C++ SDK`](https://aws.amazon.com/sdk-for-cpp/)

<a name="footnote2">3</a>. Necessary size of code and dependencies to deploy model

<a name="footnote2">4</a>. Based on [Dockerfile size](https://hub.docker.com/r/tensorflow/serving)
