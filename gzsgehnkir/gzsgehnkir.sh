cpdctl config profile set cpd --url $cpd_url --username $cpd_username --apikey $cpd_apikey
cpdctl config profile use cpd
echo "Current projects in the cluster"
echo "==============================="
cpdctl project list
EXPORT_JSON = "{'all_assets': True}"
result=$(cpdctl asset export start --project-id $project_id --assets '$EXPORT_JSON' --name demo-project-assets --output json --jmes-query "metadata.id" --raw-output)
EXPORT_ID = result.s
echo 'Export ID='=$EXPORT_ID
