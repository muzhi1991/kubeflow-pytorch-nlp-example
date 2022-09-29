#!/bin/bash

echo $#
if [ $# != 2 ]
then
    echo "Usage: ./build.sh <path-to-example> <dockerhub-username>"
    echo "Ex: ./build.sh bert muzhi1991"
    exit 1
fi

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")



## Generating current timestamp
# python3 gen_image_timestamp.py > curr_time.txt

# export images_tag=$(cat curr_time.txt)
# export images_tag=$(date '+%Y-%m-%d_%H-%M-%S')
# echo ++++ Building component images with tag=$images_tag

# full_image_name=$2/pytorch_kfp_components:$images_tag

# echo IMAGE TO BUILD: $full_image_name

# export full_image_name=$full_image_name


# ## build and push docker - to fetch the latest changes and install dependencies
# # cd pytorch_kfp_components

# docker build --no-cache -t $full_image_name .
# docker push $full_image_name

# 构建容器，这里构建了tfboard面板，apline基础容器安装了curl这些，pytorch的容器
# 在构建容器前注意修改utils/build_image.py里面的内容，registry地址，minios配置
## build tboard image (use in custom tensorboard) 修改bert.ipynb的镜像值
image_name=$2/tboard
work_dir=$SCRIPTPATH/common/tensorboard
echo "build image: ${image_name} for dir: ${work_dir}"
tboard_full_image_name=$(python utils/build_image.py $work_dir $image_name | tee /dev/tty |tail -1)
# k3d-myregistry.localhost:5000/muzhi1991/tboard:DBE73959
echo "build complete for image: ${tboard_full_image_name}"

## build alpine with some tools  修改yaml模板使用下面的镜像 pytorch_kfp_components/templates下面的模板
image_name=$2/alpine
work_dir=$SCRIPTPATH/common/alpine
echo "build image: ${image_name} for dir: ${work_dir}"
alpine_full_image_name=$(python utils/build_image.py $work_dir $image_name | tee /dev/tty |tail -1)
## k3d-myregistry.localhost:5000/muzhi1991/alpine:1171AC46
echo "build complete for image: ${alpine_full_image_name}"

## build base
image_name=$2/pytorch_kfp_components
work_dir=$SCRIPTPATH
echo "build image: ${image_name} for dir: ${work_dir}"
full_image_name=$(python utils/build_image.py $work_dir $image_name | tee /dev/tty |tail -1)
# k3d-myregistry.localhost:5000/muzhi1991/pytorch_kfp_components:B9C79655
echo "build complete for image: ${full_image_name}"
# full_image_name=k3d-myregistry.localhost:5000/muzhi1991/pytorch_kfp_components:2B1C27A7

# copy模板，根据json替换一些模板值，比如运行的cmd
python utils/generate_templates.py $1/template_mapping.json

# 替换容器镜像
## Update component.yaml files with the latest docker image name

find "yaml" -name "*.yaml" | grep -v 'copy' | grep -v "tensorboard"  | grep -v "prediction" | while read -d $'\n' file
do
    yq -i eval ".implementation.container.image =  \"$full_image_name\"" $file
done

find "yaml" -name "*.yaml" | grep -E 'tensorboard|prediction|copy'| while read -d $'\n' file
do
    yq -i eval ".implementation.container.image =  \"$alpine_full_image_name\"" $file
done

## compile pipeline

# 使用bert.ipynb而不是下面的脚本（需要修改）

# echo Running pipeline compilation
# echo "$1/pipeline.py"
# python3 "$1/pipeline.py" --target kfp
