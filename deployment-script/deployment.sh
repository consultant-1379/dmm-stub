#!/bin/bash
source VERSION
source variable.properties

function init(){
    CI_SCRIPT=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:2.0.48
    DEPLOYMENT_MANAGER=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:latest
    PACKAGE_MANAGER=armdocker.rnd.ericsson.se/proj-am/releases/eric-am-package-manager:2.92.0-1
}
function setup(){
    docker rmi -f "${CI_SCRIPT}"
    docker rmi -f "${DEPLOYMENT_MANAGER}"
    echo "CREATE NAMESPACE"
    kubectl create namespace ${NAMESPACE} 
    kubectl create secret generic eric-sec-access-mgmt-creds --from-literal=kcadminid=keycloak --from-literal=kcpasswd=Ericsson123! --from-literal=pguserid=keycloak --from-literal=pgpasswd=keycloak --namespace ${NAMESPACE}
    kubectl create secret generic eric-eo-database-pg-secret --from-literal=custom-user=eo_user --from-literal=custom-pwd=postgres --from-literal=super-user=postgres --from-literal=super-pwd=postgres --from-literal=metrics-user=exporter --from-literal=metrics-pwd=postgres --from-literal=replica-user=replica --from-literal=replica-pwd=postgres --namespace ${NAMESPACE}
    kubectl  create secret generic k8s-registry-secret --from-file=.dockerconfigjson=${DOCKER_CONFIG} --type=kubernetes.io/dockerconfigjson -n ${NAMESPACE}
    echo "PULL DEPLOYMENT MANAGER"
    docker pull "${DEPLOYMENT_MANAGER}"

}
function prepare(){

    echo "CREATE DEPLOYMENT FOLDER"
    mkdir -p ${DEPLOYMET_FOLDER}
    echo "DOWNLOAD HELMFILE"
    cd ${DEPLOYMET_FOLDER} && wget --user=${USER_NAME} --ask-password https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/eric-eiae-helmfile/eric-eiae-helmfile-${HELM_FILE_VERSION}.tgz
    echo "UNTAR HELMFILE"
    cd ${DEPLOYMET_FOLDER} && tar -xvf eric-eiae-helmfile-${HELM_FILE_VERSION}.tgz
    echo "CLONE OSS-INTERATION-CI REPO"
    cd ${DEPLOYMET_FOLDER} && git clone ssh://${USER_NAME}@gerrit.ericsson.se:29418/OSS/com.ericsson.oss.aeonic/oss-integration-ci
    echo "COPY SITE-VALUE"
    cp ${DEPLOYMET_FOLDER}/oss-integration-ci/site-values/idun/ci/template/site-values-latest.yaml ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml

}

function update_eiae_helmfile(){

    echo "CHANGE USERNAME AND PASSWORD IN REPOSITORY.YAML"
    perl -pi -e 's/\{\{ env "GERRIT_USERNAME" \}\}/'ossapps100'/' ${DEPLOYMET_FOLDER}/eric-eiae-helmfile/repositories.yaml
    perl -pi -e 's/\{\{ env "GERRIT_PASSWORD" \}\}/'OSS_too_MUCH_fun_AND_much_MORE_coming_100'/' ${DEPLOYMET_FOLDER}/eric-eiae-helmfile/repositories.yaml
    echo "UPDATE CRD"
    docker run --rm -u $(id -u):$(id -g) -v ${DEPLOYMET_FOLDER}:/ci-scripts/output-files -v ${DEPLOYMET_FOLDER}:${DEPLOYMET_FOLDER} --workdir ${DEPLOYMET_FOLDER} "${CI_SCRIPT}" script_executor update-crds-helmfile --path-to-helmfile ${DEPLOYMET_FOLDER}/eric-eiae-helmfile/crds-helmfile.yaml
    echo "TAR HELMFILE"
    cd ${DEPLOYMET_FOLDER} && tar -zvcf eric-eiae-helmfile-${HELM_FILE_VERSION}.tgz eric-eiae-helmfile

}

function update_site_value(){
    echo "UPDATE SITE-VALUE"
    perl -pi -e 's/DOCKER_REGISTRY_REPLACE/'armdocker.rnd.ericsson.se'/' ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml
    perl -pi -e 's/PASSWORD_REPLACE/'OSS_too_MUCH_fun_AND_much_MORE_coming_100'/' ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml
    perl -pi -e 's/IPV6_ENABLE_REPLACE/'false'/' ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml
    perl -pi -e 's/USERNAME_REPLACE/'ossapps100'/' ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml
    cd ${DEPLOYMET_FOLDER} && bash -c """perl -pi -e 's/IPV6_ENABLE_REPLACE/'false'/' site_values_${HELM_FILE_VERSION}.yaml;
    if [[ ${SO_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/SO_HOST_REPLACE/${SO_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${UDS_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/UDS_HOST_REPLACE/${UDS_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${LA_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/LA_HOST_REPLACE/${LA_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi;
    if [[ ${IAM_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/IAM_HOST_REPLACE/${IAM_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${PF_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/PF_HOST_REPLACE/${PF_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${ADC_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/ADC_HOST_REPLACE/${ADC_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${TA_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/TA_HOST_REPLACE/${TA_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${EAS_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/EAS_HOST_REPLACE/${EAS_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${CH_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/CH_HOST_REPLACE/${CH_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${TH_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/TH_HOST_REPLACE/${TH_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${APPMGR_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/APPMGR_HOST_REPLACE/${APPMGR_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${OS_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/OS_HOST_REPLACE/${OS_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${GAS_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/GAS_HOST_REPLACE/${GAS_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${KAFKA_BOOTSTRAP_HOST_REPLACE} != "default" ]]; then perl -pi -e 's/GAS_HOST_REPLACE/${KAFKA_BOOTSTRAP_HOST_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi;
    if [[ default != "default" ]]; then perl -pi -e 's/VNFM_HOST_REPLACE/'default'/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ default != "default" ]]; then perl -pi -e 's/VNFM_REGISTRY_HOST_REPLACE/'default'/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ default != "default" ]]; then perl -pi -e 's/HELM_CHART_HOST_REPLACE/'default'/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ default != "default" ]]; then perl -pi -e 's/GR_HOST_REPLACE/'default'/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ 0.0.0.0 != "default" ]]; then perl -pi -e 's/VNFLCM_SERVICE_IP_REPLACE/'0.0.0.0'/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ ${INGRESS_IP_REPLACE} != "default" ]]; then perl -pi -e 's/INGRESS_IP_REPLACE/${INGRESS_IP_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ default != "default" ]]; then perl -pi -e 's/EO_CM_HOST_REPLACE/'default'/' /site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ default != "default" ]]; then perl -pi -e 's/EO_CM_IP_REPLACE/'default'/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    if [[ default != "default" ]]; then perl -pi -e 's/EO_CM_ESA_IP_REPLACE/'default'/' site_values_${HELM_FILE_VERSION}.yaml; fi;
    perl -pi -e 's/VNFLCM_SERVICE_DEPLOY_REPLACE/'false'/' site_values_${HELM_FILE_VERSION}.yaml;
    perl -pi -e 's/DDP_AUTOUPLOAD_ENABLED_REPLACE/'true'/' site_values_${HELM_FILE_VERSION}.yaml;
    perl -pi -e 's/NAMESPACE/${NAMESPACE}/' site_values_${HELM_FILE_VERSION}.yaml;
    if [[ ${INGRESS_IP_REPLACE} != "default" ]]; then perl -pi -e 's/FH_SNMP_ALARM_IP_REPLACE/${INGRESS_IP_REPLACE}/' site_values_${HELM_FILE_VERSION}.yaml; fi; 
    perl -pi -e 's/HELM_REGISTRY_DEPLOY_REPLACE/'false'/' site_values_${HELM_FILE_VERSION}.yaml"""
}

function setup_for_deployment(){
    echo "UPDATE TAGS"
    docker run --init --rm  --user $(id -u):$(id -g) --volume ${DEPLOYMET_FOLDER}:/ci-scripts/output-files --volume ${DEPLOYMET_FOLDER}:/${DEPLOYMET_FOLDER} --workdir ${DEPLOYMET_FOLDER} "${CI_SCRIPT}" script_executor set-deployment-tags --deployment-tags "${APPLICATION[*]}" --state-values-file ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml
    echo "DOWNLOAD REQUIRED TGZ FILE"
    docker run --rm -v ${DEPLOYMET_FOLDER}:/ci-scripts/output-files -v ${DEPLOYMET_FOLDER}:${DEPLOYMET_FOLDER} --workdir ${DEPLOYMET_FOLDER} "${CI_SCRIPT}" script_executor get-release-details-from-helmfile --state-values-file ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml --path-to-helmfile ${DEPLOYMET_FOLDER}/eric-eiae-helmfile/helmfile.yaml --get-all-images false --fetch-charts true || exit 1
    echo "BUILD CSAR"
    cd ${DEPLOYMET_FOLDER} &&  sudo ./oss-integration-ci/ci/jenkins/scripts/build_csars_from_properties_file.sh -f ./am_package_manager.properties -d "${PACKAGE_MANAGER}" -i 'false'
    echo "CLEAN CSAR"
    docker run --init --rm  --user $(id -u):$(id -g) -v ${DEPLOYMET_FOLDER}:/ci-scripts/output-files -v ${DEPLOYMET_FOLDER}:${DEPLOYMET_FOLDER} --workdir ${DEPLOYMET_FOLDER} "${CI_SCRIPT}" script_executor cleaning-up-workspace-from-properties-file --file ${DEPLOYMET_FOLDER}/am_package_manager.properties
    echo "INITALIZED THE WORKING DIRECTORY"
    cd ${DEPLOYMET_FOLDER} && docker run --user $(id -u):$(id -g) --rm -v $PWD:/workdir --volume /etc/hosts:/etc/hosts --volume /var/run/docker.sock:/var/run/docker.sock "${DEPLOYMENT_MANAGER}" init
    echo "POPULTATE KUBE CONFIG"
    cp ${CONFIG_FILE_PATH} ${DEPLOYMET_FOLDER}/kube_config/config || exit 1;
}

function create_certificate(){

    echo "CREATE CRETIFICATES"
    cd ${DEPLOYMET_FOLDER}/certificates && bash -c """openssl req -x509 -sha256 -newkey rsa:4096 -keyout ca.key -out ca.crt -days 356 -nodes -subj '/CN=My Cert Authority';
    cp ca.crt intermediate-ca.crt;"""
    hosts=(${IAM_HOST_REPLACE} ${GAS_HOST_REPLACE} ${LA_HOST_REPLACE} ${UDS_HOST_REPLACE} ${PF_HOST_REPLACE} ${OS_HOST_REPLACE} ${APPMGR_HOST_REPLACE} ${ADC_HOST_REPLACE} ${SO_HOST_REPLACE} ${TH_HOST_REPLACE} ${TA_HOST_REPLACE} ${EAS_HOST_REPLACE} ${CH_HOST_REPLACE} ${KAFKA_BOOTSTRAP_HOST_REPLACE})
    for(( i=0; i<=${#hosts[@]}-1; i++))
    do
    if [[ ${hosts[i]} != "default" ]]; 
    then
    cd  ${DEPLOYMET_FOLDER}/certificates && bash -c """openssl req -new -newkey rsa:4096 -keyout ${hosts[i]}.key -out ${hosts[i]}.csr -nodes -subj '/CN=${hosts[i]}';
    openssl x509 -req -sha256 -days 365 -in ${hosts[i]}.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out ${hosts[i]}.crt; """
    fi;
    done

}

function prepare_final_site_value(){

    echo "PREPARE SITE-VALUE"
    cp ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml ${DEPLOYMET_FOLDER}/old_site_values_${HELM_FILE_VERSION}.yaml
    rm ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml
    docker run --init --rm  --volume /var/run/docker.sock:/var/run/docker.sock --volume ${DEPLOYMET_FOLDER}:/workdir --volume /etc/hosts:/etc/hosts --workdir ${DEPLOYMET_FOLDER} "${DEPLOYMENT_MANAGER}" prepare --namespace ${NAMESPACE} 
    docker run --rm -v ${DEPLOYMET_FOLDER}:/ci-scripts/output-files -v ${DEPLOYMET_FOLDER}:${DEPLOYMET_FOLDER} --workdir ${DEPLOYMET_FOLDER} "${CI_SCRIPT}"  script_executor merge-yaml-files --path-base-yaml ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml --path-override-yaml ${DEPLOYMET_FOLDER}/old_site_values_${HELM_FILE_VERSION}.yaml --path-output-yaml ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml --check-values-only true
    docker run --rm -v ${DEPLOYMET_FOLDER}:/ci-scripts/output-files -v ${DEPLOYMET_FOLDER}:${DEPLOYMET_FOLDER} --workdir ${DEPLOYMET_FOLDER} "${CI_SCRIPT}"  script_executor merge-yaml-files --path-base-yaml ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml --path-override-yaml ${DEPLOYMET_FOLDER}/oss-integration-ci/site-values/idun/ci/override/${OVERRIDE_SITE_VALUE} --path-output-yaml ${DEPLOYMET_FOLDER}/site_values_${HELM_FILE_VERSION}.yaml

}
init
setup
prepare
update_eiae_helmfile
update_site_value
setup_for_deployment
create_certificate
prepare_final_site_value
update_site_value











