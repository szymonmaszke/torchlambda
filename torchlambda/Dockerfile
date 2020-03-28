FROM amazonlinux:latest AS builder

ARG AWS=" "
ARG PYTORCH=" "
ARG PYTORCH_VERSION="latest"

RUN yum -y group install "Development Tools" && \
  yum -y install unzip git wget rh-python37 ninja-build cmake3 curl-devel \
  libcurl-devel libuuid-devel openssl-devel && \
  pip3 install --no-cache-dir pyyaml==5.3 && \
  ln -s /usr/bin/ninja-build /usr/bin/ninja

WORKDIR /home/app
COPY . /home/app

RUN cd dependencies && \
  ./aws-lambda.sh && \
  ./aws-sdk.sh ${AWS} && \
  ./torch.sh ${PYTORCH_VERSION} ${PYTORCH} && \
  cp -r pytorch/build_mobile/install/* /usr/local/ && \
  cp ../CMakeLists.txt ../build.sh /usr/local/

# Final image with copied install dependencies
FROM amazonlinux:latest
COPY --from=builder /usr/local /usr/local

RUN yum -y install libcurl-devel libuuid-devel openssl-devel gcc-c++ make cmake3 zip && \
      ln -s /usr/bin/ninja-build /usr/bin/ninja


LABEL maintainer="szymon.maszke@protonmail.com"

WORKDIR /usr/local

ENTRYPOINT ["./build.sh"]
CMD []
