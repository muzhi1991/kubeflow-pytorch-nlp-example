from pathlib import Path
import os
import sys

## 注意安装：
# 安装 pip install msrestazure
# 安装 pip install kubeflow-fairing #装的好慢。。安装了一堆烂七八糟的包。。
# 因为kaniko下载镜像需要走代理
# 修改文件/opt/conda/lib/python3.8/site-packages/kubeflow/fairing/builders/cluster/minio_context.py 
# 增加env， http_proxy https_proxy no_proxy
# **特别注意no_proxy需要排除minio-service.kubeflow！！！！！！！！**
#
# client.V1EnvVar(name='http_proxy',value='http://172.16.153.24:7890'),
# client.V1EnvVar(name='https_proxy',value='http://172.16.153.24:7890'),
# client.V1EnvVar(name='no_proxy',value='localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,cattle-system.svc,192.168.10.0/24,.svc,.cluster.local,example.com,localhost,.localhost,127.0.0.0/8,192.168.0.1/16,0.0.0.0,172.0.0.1/8,kubeflow-us-east-1,minio-service.kubeflow'),
# client.V1EnvVar(name='NO_PROXY',value='localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,cattle-system.svc,192.168.10.0/24,.svc,.cluster.local,example.com,localhost,.localhost,127.0.0.0/8,192.168.0.1/16,0.0.0.0,172.0.0.1/8,kubeflow-us-east-1,minio-service.kubeflow'),

from kubeflow import fairing   
from kubeflow.fairing.kubernetes.utils import mounting_pvc
import logging
from kubeflow.fairing import constants
constants.constants.KANIKO_IMAGE = "aiotceo/kaniko-executor:v1.6.0"
from kubeflow.fairing.preprocessors import base as base_preprocessor
from kubeflow.fairing.builders import cluster
from kubeflow.fairing.cloud.k8s import MinioUploader
from kubeflow.fairing.builders.cluster.minio_context import MinioContextSource

DOCKER_REGISTRY = 'k3d-myregistry.localhost:5000' # 注意nsloopup  k3d-myregistry.localhost 192.168.128.2 端口5000是k3d配置的在host上。。
minio_endpoint = "http://minio-service.kubeflow:9000/"
minio_username = "minio"
minio_key = "minio123"
minio_region = "us-east-1"
# mc config host add minio http://minio-service.kubeflow:9000 minio minio123

minio_uploader = MinioUploader(endpoint_url=minio_endpoint, minio_secret=minio_username, minio_secret_key=minio_key, region_name=minio_region)
minio_context_source = MinioContextSource(endpoint_url=minio_endpoint, minio_secret=minio_username, minio_secret_key=minio_key, region_name=minio_region)


def build_image(source_dir,image_name,registry=DOCKER_REGISTRY):
    """
    参考：https://vectorcloud.io/blog/2021/08/01/%E4%BD%BF%E7%94%A8kaniko%E6%9E%84%E5%BB%BAdocker%E9%95%9C%E5%83%8F/

    """
    output_map =  {
    }
    source_dir_path=Path(source_dir)
    if not source_dir_path.exists():
        raise Exception(f"not find source_dir:{source_dir}")
        
    dockerfile_path=Path(os.path.join(source_dir,"Dockerfile"))
    if not dockerfile_path.exists():
        raise Exception(f"not find Dockerfile:{dockerfile_path}")
                         
    for p in source_dir_path.rglob("*"):
        target_path = os.path.relpath(p, source_dir)
        output_map[p]=target_path
        print(p,"-->",target_path)

    preprocessor = base_preprocessor.BasePreProcessor(
        command=["python"], # The base class will set this.
        input_files=[],
        path_prefix="/app", # irrelevant since we aren't preprocessing any files
        output_map=output_map)

    preprocessor.preprocess()
  
    cluster_builder = cluster.cluster.ClusterBuilder(registry=registry,
                                                     base_image="", # base_image is set in the Dockerfile
                                                     preprocessor=preprocessor,
                                                     image_name=image_name,
                                                     dockerfile_path="Dockerfile",
                                                     context_source=minio_context_source)
    cluster_builder.build()
    return cluster_builder.image_tag

if __name__ == "__main__":
    if len(sys.argv) == 3:
        source_dir = sys.argv[1]
        image_name = sys.argv[2]
        full_image_name=build_image(source_dir,image_name)
        # sys.stderr.write(full_image_name)
        print(full_image_name)
    elif len(sys.argv) == 4:
        source_dir = sys.argv[1]
        image_name = sys.argv[2]
        registry = sys.argv[3]
        full_image_name=build_image(source_dir,image_name,registry)
        # sys.stderr.write(full_image_name)
        print(full_image_name)
    else:
        raise Exception(
            f"\n\nUsage: "
            f"python utils/build_image.py "
            f"source_dir image_name [registry] \n\n default registry is {DOCKER_REGISTRY} \n\n"
        )