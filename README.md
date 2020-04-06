<img align="left" width="256" height="256" src="https://github.com/szymonmaszke/torchlambda/blob/master/assets/banner.png">

[__torchlambda__](https://szymonmaszke.github.io/torchlambda/) is a tool to deploy [PyTorch](https://pytorch.org/) models
on [Amazon's AWS Lambda](https://aws.amazon.com/lambda/) using [AWS SDK for C++](https://aws.amazon.com/sdk-for-cpp/)
and [custom C++ runtime](https://github.com/awslabs/aws-lambda-cpp).

Using statically compiled dependencies __whole package is shrunk to only `30MB`__.

Due to small size of compiled source code users can pass their models as [AWS Lambda layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).
__Services like [Amazon S3](https://aws.amazon.com/s3/) are no longer necessary to load your model__.

[__torchlambda__](https://szymonmaszke.github.io/torchlambda/) has it's PyTorch & AWS dependencies always up to date because of [continuous deployment](https://en.wikipedia.org/wiki/Continuous_deployment) run at `03:00 a.m.`
every day.


| Docs | Status | Package | Python | PyTorch | Docker | CodeBeat | Images |
|------|--------|---------|--------|---------|--------|----------|--------|
|[![Documentation](https://img.shields.io/static/v1?label=&message=Wiki&color=EE4C2C&style=for-the-badge)](https://github.com/szymonmaszke/torchlambda/wiki) | ![CD](https://img.shields.io/github/workflow/status/szymonmaszke/torchlambda/tests?label=%20&style=for-the-badge) | [![PyPI](https://img.shields.io/static/v1?label=&message=PyPI&color=377EF0&style=for-the-badge)](https://pypi.org/project/torchlambda/) | [![Python](https://img.shields.io/static/v1?label=&message=>=3.6&color=377EF0&style=for-the-badge&logo=python&logoColor=F8C63D)](https://www.python.org/) | [![PyTorch](https://img.shields.io/static/v1?label=&message=>=1.4.0&color=EE4C2C&style=for-the-badge)](https://pytorch.org/) | [![Docker](https://img.shields.io/static/v1?label=&message=>17.05&color=309cef&style=for-the-badge)](https://cloud.docker.com/u/szymonmaszke/repository/docker/szymonmaszke/torchlambda) | [![codebeat badge](https://codebeat.co/badges/ca6f19c8-29ad-4ddb-beb3-4d4e2fb3aba2)](https://codebeat.co/projects/github-com-szymonmaszke-torchlambda-master) | [![Images](https://img.shields.io/static/v1?label=&message=Tags&color=309cef&style=for-the-badge)](https://hub.docker.com/r/szymonmaszke/torchlambda/tags)|


# Comparison with other deployment tools

__Improve this comparison's reliability via [Pull Request](https://github.com/szymonmaszke/torchlambda/pulls?q=is%3Apr+is%3Aopen+sort%3Aupdated-desc), thanks.
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
__Version (higher more mature)__ | [CD](https://en.wikipedia.org/wiki/Continuous_deployment) | N/A | [1.0](https://github.com/kubeflow/kubeflow/releases/tag/v1.0) | [2.1.0](https://github.com/tensorflow/serving/releases/tag/2.1.0) |
__Customizable dependencies__ <sup>[2](#footnote2)</sup> | :heavy_check_mark: | :x: | :x: | :x: |
__Deployment size__ <sup>[3](#footnote3)</sup>| ~30Mb| +1Gb | N/A | ~67Mb<sup>[4](#footnote4)</sup> |

# Table Of Contents

- [Installation](https://github.com/szymonmaszke/torchlambda/wiki/Installation)
- [Tutorials](https://github.com/szymonmaszke/torchlambda/wiki/Tutorials)
	- [Basic deployment on AWS Lambda]()
	- [`base64` image encoding]()
	- [Testing your function locally]()
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
