mkdir data
oc logs -n openshift-operator-lifecycle-manager $(oc get pods -n openshift-operator-lifecycle-manager -lapp=catalog-operator -o name)>data/olm-status.log