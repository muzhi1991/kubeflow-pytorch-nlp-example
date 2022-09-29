ARG http_proxy="http://172.16.153.24:7890"
ARG https_proxy="http://172.16.153.24:7890"

FROM alpine:latest

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

RUN apk add curl
RUN apk add jq


ENV http_proxy=
ENV https_proxy=
RUN unset http_proxy https_proxy