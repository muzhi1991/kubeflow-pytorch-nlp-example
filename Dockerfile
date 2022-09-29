# Copyright (c) Facebook, Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG BASE_IMAGE=pytorch/pytorch:latest
ARG http_proxy="http://172.16.153.24:7890"
ARG https_proxy="http://172.16.153.24:7890"

FROM ${BASE_IMAGE}

COPY . .

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

RUN pip install -U pip

RUN pip install -U --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y vim && apt-get install -y git
RUN git clone https://github.com/kubeflow/pipelines.git
RUN pip install pipelines/components/PyTorch/pytorch-kfp-components/.

# RUN pip install pytorch-kfp-components

ENV http_proxy=
ENV https_proxy=
RUN unset http_proxy https_proxy

ENV PYTHONPATH /workspace

ENTRYPOINT /bin/bash
