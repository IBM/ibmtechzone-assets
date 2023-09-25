product=$1
OC_LOGIN=$2
#Login to OpenShift Custer
$OC_LOGIN

#Create new project
oc new-project code-server

#Bring project in focus
oc project code-server

#Create service account with admin controls
oc create serviceaccount code-server-sa
oc adm policy add-scc-to-user privileged -z code-server-sa
oc adm policy add-cluster-role-to-user cluster-admin -z code-server-sa

#Deploy the image
oc apply -f deployment.yaml
sleep 5

while ! oc get pod -l app=code-server-ui --no-headers | grep -m 1 "Running";do
  sleep 1
done

#Select product to load as env variable
oc set env deployment/code-server-ui DEFAULT_PRODUCT_NAME=$product
#Create a service
oc apply -f service.yaml 
sleep 5

#expose the service
oc apply -f route.yaml 
sleep 5
echo "Access the Deployer at : "
routes=( $(oc get route code-server-ui-route --no-headers) )
echo "https://${routes[1]}"
