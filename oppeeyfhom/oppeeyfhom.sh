project_uuid=$(cat /proc/sys/kernel/random/uuid)
cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
echo "Check if DataGovernance already exists"
echo "===================================="
project_id=$(cpdctl project list --name="DataGovernance" --output json -j "(resources[].metadata.guid)[0]" --raw-output)
cpdctl project delete --project-id $project_id
storage_json="{\"type\": \"assetfiles\", \"guid\": \"$project_uuid\"}"
cpdctl project create --name "DataGovernance" --output json --raw-output --storage '$storage_json' --jmes-query 'location'
cpdctl project list
project_id=$(cpdctl project list --name="DataGovernance" --output json -j "(resources[].metadata.guid)[0]" --raw-output)
cpdctl asset import start --project-id $project_id --import-file DataGovernance.zip --output json --jmes-query "metadata.id" --raw-output

