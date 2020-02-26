FROM amazonlinux:latest AS builder

RUN yum -y group install "Development Tools" && \
  yum -y install unzip git cmake3 curl-devel wget rh-python37 ninja-build && \
  pip3 install --no-cache-dir pyyaml==5.3

WORKDIR /home/app
COPY . /home/app

RUN ./dependencies.sh

CMD ["./build.sh"]
