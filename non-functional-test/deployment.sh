KUBECONFIG=$1
NAMESPACE=$2
SERVICE_NAME=$3
SCALE=$4
SERVICE_OVERIDE=$5
REPO_NAME=$6
REPO_PATH=$7
USER_NAME=$8
PASSWORD=$9
INSTALL_VERSION=${10}
UPGRADE_VERSION=${11}
API_TEST=${12}

function init(){
    random_string=$(openssl rand -base64 12)
    SERVICE_OVERIDE=$(echo "$SERVICE_OVERIDE" | sed 's/[(|)]//g')
    IFS=',' read -ra SERVICE_NAME <<< "$SERVICE_NAME"
    # Separate the values with commas and store them in an array
    IFS=',' read -r -a SERVICE_OVERIDE <<< "$SERVICE_OVERIDE"
    IFS=',' read -ra SCALE <<< "$SCALE"
    IFS=',' read -ra UPGRADE_VERSION <<< "$UPGRADE_VERSION"
}
#install
function install(){
    echo $PASSWORD
    helm repo remove $REPO_NAME || true
    echo "helm repo add $REPO_NAME $REPO_PATH --username=$USER_NAME --password=$PASSWORD"
    helm repo add $REPO_NAME $REPO_PATH --username $USER_NAME --password $PASSWORD
    helm uninstall $REPO_NAME --namespace $NAMESPACE --kubeconfig $KUBECONFIG || true
    kubectl create namespace $NAMESPACE --kubeconfig $KUBECONFIG || true
    user=$(echo ~)
    kubectl create secret generic k8s-registry-secret --from-file=.dockerconfigjson=$user/.docker/config.json --type=kubernetes.io/dockerconfigjson --namespace $NAMESPACE --kubeconfig $KUBECONFIG || true
    SECONDS=0
    echo "helm install $REPO_NAME $REPO_PATH/$REPO_NAME --version $INSTALL_VERSION -f site_values.yaml --namespace $NAMESPACE --kubeconfig $KUBECONFIG --wait --debug"
    helm install $REPO_NAME $REPO_NAME/$REPO_NAME --version $INSTALL_VERSION -f site_values.yaml --namespace $NAMESPACE --kubeconfig $KUBECONFIG --wait --debug
    echo "install done with $INSTALL_VERSION = pass" >> deployment.properties
    total_time=`echo "scale=2; $SECONDS/60" | bc`
    echo "install duration for $INSTALL_VERSION = ${total_time}min" >> characteristics.properties
}
#upgrade
function upgrade(){
    for (( i=0; i<${#UPGRADE_VERSION[@]}; i++ ));
    do
      SECONDS=0
      helm upgrade $REPO_NAME $REPO_NAME/$REPO_NAME --version ${UPGRADE_VERSION[i]} -f site_values.yaml --namespace $NAMESPACE --kubeconfig $KUBECONFIG --wait --debug
      total_time=`echo "scale=2; $SECONDS/60" | bc`
      echo "upgrade duration for ${UPGRADE_VERSION[i]} = ${total_time}min" >> characteristics.properties
      echo "multiple upgrade done with ${UPGRADE_VERSION[i]} = pass ">> deployment.properties
    done
}

#rollback
function rollback(){
    helm rollback $REPO_NAME 1 --namespace $NAMESPACE --kubeconfig $KUBECONFIG --wait --debug
    total_time=`echo "scale=2; $SECONDS/60" | bc`
    echo "rollback duration  = ${total_time}min" >> characteristics.properties
    echo "rollback done = pass" >> deployment.properties
}

#api testing
function api_test(){
    if [[ $API_TEST == True ]]
    then
        stop_connection(){
          PID=$(ps -ef | grep kubectl | grep port-forward | grep ${port} | awk {'print $2'})
          kill $PID
        }
        for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
        do
          service_count=$(jq -r '."'${SERVICE_NAME[i]}'" | keys | length' data.json)
          for (( j=1; j<=${service_count}; j++ ))
          do
            method=$(jq -r '."'${SERVICE_NAME[i]}'"."'$j'"."METHOD"' data.json)
            payload=$(jq -r '."'${SERVICE_NAME[i]}'"."'$j'"."PAYLOAD"' data.json)
            path=$(jq -r '."'${SERVICE_NAME[i]}'"."'$j'"."PATH"' data.json)
            port=$(jq -r '."'${SERVICE_NAME[i]}'"."'$j'"."PORT"' data.json)
            head=$(jq -r '."'${SERVICE_NAME[i]}'"."'$j'"."HEAD"' data.json)
            status=$(jq -r '."'${SERVICE_NAME[i]}'"."'$j'"."STATUS"' data.json)
            echo ${port}
            POD_NAME=$(kubectl get pod -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | awk {'print $1'}| head -n 1)
            echo ${POD_NAME}
            kubectl port-forward ${POD_NAME} 8086:${port} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} &
            sleep 5
            #curl -v -X -i --request ${method} http://localhost:8084/${path} --header "${head}" --data "${payload}"
            status_code=$(curl --write-out "%{http_code}" --silent --output /dev/null -X ${method} http://localhost:8086/${path} -H "${head}" -d "${payload}")
            echo $status_code
            if [[ $status_code == $status ]]
            then
                echo "${SERVICE_NAME[i]}-$j-ISSU-test = pass" >> deployment.properties
            else
                echo "${SERVICE_NAME[i]}-$j-ISSUE-test = fail" >> deployment.properties
                stop_connection
                # exit 1
            fi
            stop_connection
          done
        done
    fi
}


#scale
function scale(){
      echo ${SERVICE_OVERIDE[@]}
      echo ${SERVICE_NAME[@]}
      for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
      do
      if [[ -n "${SERVICE_OVERIDE[i]}" ]]
      then
          echo "inside if"
          echo ${SERVICE_NAME[i]}
          echo ${SERVICE_OVERIDE[i]}
          SERVICE_NAME[i]=${SERVICE_OVERIDE[i]}
      fi
      done
      echo ${SERVICE_NAME[@]}
      for (( i=0; i<${#SERVICE_NAME[@]}; i++ ));
      do
        if [ "${SERVICE_NAME[i]}" != "except" ]; then
          echo "service name - ${SERVICE_NAME[i]}"
          json_value=$(kubectl get deploy ${SERVICE_NAME[i]} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} -o json)
          get_replicas=$(echo $json_value | jq -r .spec.replicas)
          echo "kubectl scale deploy ${SERVICE_NAME[i]} --replicas ${SCALE[i]} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}"
          kubectl scale deploy ${SERVICE_NAME[i]} --replicas ${SCALE[i]} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}
          sleep 10
          POD_COUNT=$(kubectl get po -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} | grep ${SERVICE_NAME[i]} | wc -l)
            if [ "$POD_COUNT" == "${SCALE[i]}" ]; then
              echo "${SERVICE_NAME[i]} service scaled = pass" >> deployment.properties
              kubectl scale deploy ${SERVICE_NAME[i]} --replicas ${get_replicas} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}
            else
              echo "${SERVICE_NAME[i]} service scaled = fail" >> deployment.properties
              kubectl scale deploy ${SERVICE_NAME[i]} --replicas ${get_replicas} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}
            fi
          fi
      done
}

init
install
upgrade
rollback
api_test
scale
sleep 30