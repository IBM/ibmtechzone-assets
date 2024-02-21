cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
echo "Check if DataGovernance already exists"
echo "===================================="
project_id=$(cpdctl project list --name="DataGovernance" --output json -j "(resources[].metadata.guid)[0]" --raw-output)

EXPORT_JSON = "{'all_assets': True}"
result=$(cpdctl asset export start --project-id $project_id --assets '$EXPORT_JSON' --name datagovernance-project-assets --output json --jmes-query "metadata.id" --raw-output)
export_id = result.s
echo 'Export ID='=$EXPORT_ID

cpdctl asset export download --project-id $project_id --export-id $export_id --output-file project-assets.zip --progress

