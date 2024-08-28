#!/bin/bash

KUBECONFIG=$1
NAMESPACE=$2
SERVICE_NAME=$3

function init(){
    IFS=',' read -ra SERVICE_NAME <<< "$SERVICE_NAME"
}
#cpu and memory
function resource(){
    for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
    do
        echo "calculating CPU and MEMORY for ${SERVICE_NAME[i]}"
        POD_COUNT_RESOURCE=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | wc -l)
        POD_NAME_RESOURCE=$(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $1'} | tr '\n' ' ')
        POD_NAME_RESOURCE_ARR=($POD_NAME)
        for (( j=0; j<${#POD_NAME_RESOURCE_ARR[@]}; j++ ));
        do
            CPU=$(kubectl top pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${POD_NAME_RESOURCE_ARR[j]} | awk {'print $2'})
            MEMORY=$(kubectl top pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${POD_NAME_RESOURCE_ARR[j]} | awk {'print $3'})
            echo "CPU for ${POD_NAME_ARR[j]} = $CPU ">> characteristics.properties
            echo "MEMORY for ${POD_NAME_ARR[j]} = $MEMORY" >> characteristics.properties

        done
    done
}

# image size
function images_size(){
    UNIQUE_IMAGE_NAME=()
    for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
    do
        mapfile -t POD_NAME_IMAGE < <(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $1'} )
        for (( j=0; j<${#POD_NAME_IMAGE[@]}; j++ ));
        do
            echo ${POD_NAME_IMAGE[j]}
            JSON_POD=$(kubectl get po ${POD_NAME_IMAGE[j]}  --kubeconfig ${KUBECONFIG} -n ${NAMESPACE} -o json)
            mapfile -t IMAGE_NAME < <(echo "$JSON_POD" | jq -r '.spec.containers[].image')
            echo ${IMAGE_NAME[@]}
            for uniq in ${IMAGE_NAME[@]} ;
            do
                if [[ ! " ${UNIQUE_IMAGE_NAME[@]} " =~ " $uniq " ]]; then
                    UNIQUE_IMAGE_NAME+=("$uniq")
                    echo "inside"
                fi
            done
        done
    done
    echo "list of image"
    echo ${UNIQUE_IMAGE_NAME[@]}
    for IMAGE in ${UNIQUE_IMAGE_NAME[@]}
    do
        if grep -q ${IMAGE} characteristics.properties; then
            echo "${IMAGE} already exists in characteristics.properties"
        else
        docker pull ${IMAGE}
        IMAGE_SIZE=$(docker images ${IMAGE} | tail -n 1 | awk {'print $7'})
        echo "${IMAGE}  image size = $IMAGE_SIZE " >> characteristics.properties
        fi
    done
}

init
resource
images_size
