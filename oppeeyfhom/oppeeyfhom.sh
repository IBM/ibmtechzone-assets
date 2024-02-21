project_uuid=$(cat /proc/sys/kernel/random/uuid)
cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
echo "Check if DataGovernance already exists"
echo "===================================="
project_id=$(cpdctl project list --name="DataGovernance" --output json -j "(resources[].metadata.guid)[0]" --raw-output)
if test "$project_id" = "null"
then
    echo "Project does not exist"
else
    cpdctl project delete --project-id $project_id
fi

storage_json="{\"type\": \"assetfiles\", \"guid\": \"$project_uuid\"}"
echo $storage_json
cpdctl project create --name "DataGovernance" --output json --raw-output --storage "$storage_json" --jmes-query 'location'
cpdctl project list
project_id=$(cpdctl project list --name="DataGovernance" --output json -j "(resources[].metadata.guid)[0]" --raw-output)
cpdctl asset import start --project-id $project_id --import-file DataGovernance.zip --output json --jmes-query "metadata.id" --raw-output
connection_id=$(cpdctl connection list --project-id $project_id --output json -j "(resources[0].metadata.asset_id)" --raw-output)

concat_string=$cpd_username
concat_string+=":"
concat_string+=$cpd_apikey

cpd_token=$(echo $concat_string|base64)

rm -rf cp4d_info.conf
echo "[CP4D]">>cp4d_info.conf
echo "CPD_URL="$cpd_url>>cp4d_info.conf
echo "CPD_USERNAME="$cpd_username>>cp4d_info.conf
echo "CPD_TOKEN="$cpd_token>>cp4d_info.conf
echo "CP4D_APIKEY="$cpd_apikey>>cp4d_info.conf
echo "CONNECTION_ID="$connection_id>>cp4d_info.conf
