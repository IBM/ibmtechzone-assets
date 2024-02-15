cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
echo "Create new project for Data and AI called DataProject"
echo "======================================================"
project_uuid=$(uuidgen)
STORAGE="{\"type\": \"assetfiles\", \"guid\": \"$project_uuid\"}"
PROJECT_CREATION=cpdctl project create --name "DataProject" --output json --raw-output --generator cli --storage '{STORAGE_JSON}' -j 'location'
echo $PROJECT_CREATION
echo "Create new connections for Data and AI called DataProject"


