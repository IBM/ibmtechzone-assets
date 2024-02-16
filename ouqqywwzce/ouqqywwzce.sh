cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
echo "Check if DataProject already exists"
echo "===================================="
DATAPROJECT_EXISTS=$(cpdctl project list --name="DataProject" --output json -j "(resources[].metadata.guid)[0]" --raw-output)
if test "$DATAPROJECT_EXISTS" = "null"
then
    echo "DataProject does not exist so create it"
    echo "Create new project for Data and AI called DataProject"
    echo "======================================================"
    project_uuid=$(cat /proc/sys/kernel/random/uuid)
    STORAGE="{\"type\": \"assetfiles\", \"guid\": \"$project_uuid\"}"
    PROJECT_CREATION=$(cpdctl project create --name "DataProject" --output json --raw-output --generator cli --storage "$STORAGE" -j 'location')
else
    echo "DataProject exists with Project UID=$DATAPROJECT_EXISTS"
fi
echo "Create new connections for Data and AI called DataProject"

CREATE_CONN_PROPERTIES="{\"database\": \"$database_name\",\"host\": \"$database_host\",\"port\": \"$database_port\",\"password\": \"$database_password\",\"username\": \"$database_user\"}"
echo $CREATE_CONN_PROPERTIES
CONNECTION_ID=$(cpdctl connection create --name "datasource-connection" --description "Connection to my datasource" --datasource-type "$datasource_type" --project-id "$DATAPROJECT_EXISTS" --properties "$CREATE_CONN_PROPERTIES" -j metadata.asset_id --origin-country us --output json -j 'metadata.asset_id')
echo $CONNECTION_ID
ALL_TABLES=$(cpdctl connection discover-adhoc --path="/gosalesdw" --datasource-type "$datasource_type" --name "datasource-connection" --properties "$CREATE_CONN_PROPERTIES" --output json)
echo $ALL_TABLES|jq '.assets[].id'
ASSET_METADATA="{\"name\": \"emp_expense_fact\",\"asset_type\": \"data_asset\",\"origin_country\": \"us\",\"asset_category\": \"USER\"}"
ASSET_ENTITY="{\"data_asset\": {\"mime_type\": \"application/x-ibm-rel-table\",\"dataset\": true},\"discovered_asset\": {   \"extended_metadata\": [{\"name\":\"table_type\",\"value\":\"TABLE\"}]}}"
ATTACHMENTS='[{"asset_type": "data_asset","connection_id": "$CONNECTION_ID","connection_path": "/gosalesdw/emp_expense_fact/"}]'
echo $ATTACHMENTS
cpdctl asset data-asset create --project-id "$DATAPROJECT_EXISTS" --metadata "$ASSET_METADATA" --entity "$ASSET_ENTITY" --attachments "$ATTACHMENTS" --output json -j metadata.asset_id