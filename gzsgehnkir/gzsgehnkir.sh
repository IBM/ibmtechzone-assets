cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
echo "Check if DataGovernance already exists"
echo "===================================="
project_id=$(cpdctl project list --name="DataGovernance" --output json -j "(resources[].metadata.guid)[0]" --raw-output)
echo $project_id
export_json="{\"all_assets\": true}"
export_id=$(cpdctl asset export start --project-id $project_id --assets "$export_json" --name datagovernance-project-assets  --output json -j "(metadata.id)" --raw-output)
echo $export_id
echo 'Export ID='=$export_id
cpdctl asset export download --project-id $project_id --export-id $export_id --output-file DataGovernance.zip --progress

