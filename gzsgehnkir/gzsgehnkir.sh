EXPORT_JSON = "{'all_assets': True}"
result=$(cpdctl asset export start --project-id $project_id --assets '$EXPORT_JSON' --name demo-project-assets --output json --jmes-query "metadata.id" --raw-output)
EXPORT_ID = result.s
echo 'Export ID='=$EXPORT_ID
