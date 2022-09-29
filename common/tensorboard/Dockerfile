ARG http_proxy="http://172.16.153.24:7890"
ARG https_proxy="http://172.16.153.24:7890"
FROM gcr.io/deeplearning-platform-release/tf2-cpu.2-2:latest
# FROM python:3.8-alpine

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy


RUN pip install --user --no-cache-dir boto3

RUN pip install --user --no-cache-dir torch-tb-profiler

ENV http_proxy=
ENV https_proxy=
RUN unset http_proxy https_proxy