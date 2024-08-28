#!/bin/bash
source variable.properties
# Delete namespace
if kubectl get ns ${NAMESPACE} ; then
  echo "Deleting Namespace...."
  kubectl delete ns $NAMESPACE 
else
  echo "namespace does not exist..."
fi

# Delete ClusterRoles associated with namespace
cluster_role_names=$(kubectl  get clusterroles -o=jsonpath="{.items[?(@.metadata.annotations.meta\.helm\.sh\/release-namespace=='${NAMESPACE}')].metadata.name}")
if [[ "${cluster_role_names}" != "" ]]; then
  echo "Deleting Cluster Roles..."
  kubectl delete clusterroles $cluster_role_names 
fi

# Delete ClusterRoleBindings associates with namespace
cluster_role_binding_names=$(kubectl get clusterrolebindings -o=jsonpath="{.items[?(@.metadata.annotations.meta\.helm\.sh\/release-namespace=='${NAMESPACE}')].metadata.name}")
if [[ "${cluster_role_binding_names}" != "" ]]; then
  echo "Deleting Cluster Role Bindings..."
  kubectl delete clusterrolebindings $cluster_role_binding_names 
fi
