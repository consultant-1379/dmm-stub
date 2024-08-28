#!/bin/bash
KUBECONFIG=$1
NAMESPACE=$2
SERVICE_NAME=$3
DEPENDENT_SERVICE=$4
REPO_NAME=$5
UPGRADE_VERSION=$6

function init(){
    IFS=',' read -ra SERVICE_NAME <<< "$SERVICE_NAME"
    IFS=',' read -ra UPGRADE_VERSION <<< "$UPGRADE_VERSION"
    DEPENDENT_SERVICE=$(echo "$DEPENDENT_SERVICE" | sed 's/^\[//' | sed 's/\]$//')
    IFS=',' read -ra DEPENDENT_SERVICE <<< "$DEPENDENT_SERVICE"
    random_string=$(openssl rand -base64 12)
}


#service restart
function service_restart(){
    for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
    do
      echo "calculating restart time for ${SERVICE_NAME[i]}"
      POD_COUNT_SERVICE_RESTART=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | wc -l)
      echo "pod count - $POD_COUNT"
      CONTAINER_STATUS_SERVICE_RESTART=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $2'}| head -n 1)
      echo "constainer status - $CONTAINER_STATUS_SERVICE_RESTART"
      echo "kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $1'} | tr '\n' ' '"
      POD_NAME_SERVICE_RESTART=$(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $1'} | tr '\n' ' ')
      IFS=' ' read -ra POD_NAME_SERVICE_RESTART_ARR <<< "$POD_NAME_SERVICE_RESTART"
      echo ${POD_NAME_SERVICE_RESTART_ARR[@]}
      POD_ARRAY_SERVICE_RESTART=()
      echo "pod name -${POD_NAME_SERVICE_RESTART_ARR[@]}"
      for POD in ${POD_NAME_SERVICE_RESTART_ARR[@]};
      do
        if [ -z $(kubectl get pod ${POD} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} -o jsonpath='{.metadata.labels.job-name}') ]; then
        POD_ARRAY_SERVICE_RESTART+=(${POD})
        fi
      done
      echo "pod array - ${POD_ARRAY_SERVICE_RESTART[@]}"
      SECONDS=0
      kubectl delete po ${POD_ARRAY_SERVICE_RESTART[@]} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}
      echo "SIGTERM and SIGKILL handling , deleting $POD_NAME_SERVICE_RESTART_ARR pods duration = ${SECONDS}Seconds " >>robustness.properties
      SECONDS=0
      while true
      do
          OUTPUT=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | grep $CONTAINER_STATUS_SERVICE_RESTART | wc -l)
        if [ "${#POD_ARRAY_SERVICE_RESTART[@]}" == "$OUTPUT" ]; then
          break;
        fi
    done
    echo "total time taken ${SERVICE_NAME[i]} $SECONDS"
    echo "${SERVICE_NAME[i]}_RESTART = ${SECONDS}Seconds" >> robustness.properties
    done
}

#dependend service 
function dep_sevice_restart(){
    echo "dependend service -$DEPENDENT_SERVICE"
    for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
    do
    echo "calculating restart time for ${SERVICE_NAME[i]} with dependency delete"
    POD_COUNT_DEP_RESTART=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | wc -l)
    CONTAINER_STATUS_DEP_RESTART=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $2'}| head -n 1)
    echo "dep status - $CONTAINER_STATUS_DEP_RESTART"
    POD_NAME_DEP_RESTART=$(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep -e ${SERVICE_NAME[i]}  | awk {'print $1'} | tr '\n' ' ')
    echo "kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep -e ${SERVICE_NAME[i]}  | awk {'print $1'} | tr '\n' ' '"
    DEP_POD_NAME=()
    echo ${POD_NAME_DEP_RESTART[@]}
    POD_ARRAY_DEP_RESTART=()
    echo "pod name -${POD_NAME_DEP_RESTART[@]}"
    echo "service name - ${SERVICE_NAME[i]}"
    for POD_DEP_RESTART in ${POD_NAME_DEP_RESTART[@]};
    do
      if [ -z $(kubectl get pod ${POD_DEP_RESTART} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} -o jsonpath='{.metadata.labels.job-name}') ]; then
      POD_ARRAY_DEP_RESTART+=(${POD_DEP_RESTART})
      fi
    done
    echo "pod array - ${POD_ARRAY_DEP_RESTART[@]}"
    string=$(echo ${DEPENDENT_SERVICE[i]} | tr -d '()')
    IFS=' ' read -ra string <<< "${string}"
    for (( j=0; j<${#string[@]}; j++ ));
    do
    DEP_POD_NAME[j]=$(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep -e ${string[j]} | awk {'print $1'} | tr '\n' ' ')
    done
    kubectl delete po ${POD_ARRAY_DEP_RESTART[@]} ${DEP_POD_NAME[@]} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}
    SECONDS=0
    while true
    do
        OUTPUT=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | grep $CONTAINER_STATUS_DEP_RESTART | wc -l)
        echo "output - $OUTPUT"
      if [ "${#POD_ARRAY_DEP_RESTART[@]}" == "$OUTPUT" ]; then
        break;
      fi
    done
    echo "total time taken ${SERVICE_NAME[i]} with dependend service $SECONDS"
    echo "${SERVICE_NAME[i]}_RESTART_WITH_DEPENDEND_SERVICE = ${SECONDS}Seconds" >> robustness.properties
    done
}

#liveness
function liveness_readiness(){
for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
do
POD_NAME_LIVENESS=$(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $1'} | head -n 1)
DESCRIBE_POD=$(kubectl describe po $POD_NAME_LIVENESS -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep -E "Liveness:|Readiness:")
  if [ -n "$DESCRIBE_POD" ]; then
    echo "container  ${SERVICE_NAME[i]} have liveness = pass" >> robustness.properties
  else
    echo "container  ${SERVICE_NAME[i]}  have liveness = fail" >> robustness.properties
  fi
done
}

init
service_restart
dep_sevice_restart
liveness_readiness