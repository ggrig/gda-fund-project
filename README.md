# GDA fund project

## Prerequisites for building on Ubuntu 20.04

Clone the repo
```
    git clone https://github.com/ggrig/gda-fund-project.git
    git submodule update --init --recursive
```

Install build tools  

```
    sudo apt-get update
    sudo apt  install cmake
    sudo apt-get install build-essential
    sudo apt-get install libssl-dev
    sudo apt install zlib1g-dev
```

Build & install libwebsockets  

```
    cd libwebsockets/
```
Fix a confuguration bug in the librarary source  

Open `libwebsockets/CMakeLists.txt` and change  

```
    ...
    option(LWS_WITH_SECURE_STREAMS "Secure Streams protocol-agnostic API" OM)
    ...
```
to
```
    ...
    option(LWS_WITH_SECURE_STREAMS "Secure Streams protocol-agnostic API" ON)
    ...
```
Enable Extensions
```
    option(LWS_WITHOUT_EXTENSIONS "Don't compile with extensions" OFF)
```

## Build the library
```
    make .
    make && sudo make install
```
## Install Docker
```
    cd Docker
    ./install-docker.sh
```
Verify docker has been installed
```
    docker -v
    Docker version 20.10.8, build 3967b7d
```
## Build the docker image with Amazon Kinesis Agent
```
    sudo docker image build -t gdafund/bybit:0.01 ./Docker
```

