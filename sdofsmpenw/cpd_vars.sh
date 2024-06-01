export OPENSHIFT_BASE_DOMAIN=<BASE DOMAIN> #662a60257a54bb001e245056.cloud.techzone.ibm.com
IBM_ENTITLEMENT_KEY=<YOUR IBM_ENTITLEMENT_KEY>
export OCP_URL=api.${OPENSHIFT_BASE_DOMAIN}:6443
export OCP_USERNAME=kubeadmin
export OCP_PASSWORD=<OCP_PASSWORD>
export VERSION=4.8.3
export STG_CLASS_BLOCK=ocs-storagecluster-ceph-rbd
export STG_CLASS_FILE=ocs-storagecluster-cephfs
export LOGIN_ARGUMENTS="--username=${OCP_USERNAME} --password=${OCP_PASSWORD}"
export PROJECT_CPD_INST_OPERATORS=cpd-operators
export PROJECT_CPD_INST_OPERANDS=cpd-instance
export PROJECT_CERT_MANAGER=cert-manager
export PROJECT_LICENSE_SERVICE=cpd-license
export PROJECT_SCHEDULING_SERVICE=cpd-scheduling
export PATH="./cpd-cli-linux-EE-13.1.5-176":$PATH
export COMPONENTS=watsonx_governance