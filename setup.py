import pathlib

import setuptools


def read(filepath, variable):
    namespace = {}
    exec(open(filepath).read(), namespace)
    return namespace[variable]


setuptools.setup(
    name="torchlambda",
    version=read("torchlambda/_version.py", "__version__"),
    license="MIT",
    author="Szymon Maszke",
    author_email="szymon.maszke@protonmail.com",
    description="Minimalistic & easy deployment of PyTorch models on AWS Lambda with C++",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/torchlambda",
    packages=setuptools.find_packages(),
    package_data={"": ["*.sh", "*.txt", "Dockerfile", ".dockerignore", "templates"]},
    python_requires=">=3.6",
    install_requires=["PyYAML>=5.3", "Cerberus>=1.3.2"],
    entry_points={"console_scripts": ["torchlambda=torchlambda.main:main"],},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Website": "https://szymonmaszke.github.io/torchlambda",
        "Documentation": "https://szymonmaszke.github.io/torchlambda/#torchlambda",
        "Issues": "https://github.com/szymonmaszke/torchlambda/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc",
    },
    keywords="aws lambda pytorch deployment minimal c++ neural network model",
)
