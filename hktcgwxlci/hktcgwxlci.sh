export AWS_CLI="$(pwd)"
export PATH=$PATH:$AWS_CLI/aws/v2/current/bin
echo "[default]
aws_access_key_id = $s3_access_key
aws_secret_access_key = $s3_secret_key 
region = $s3_region 
endpoint_url = $s3_endpoint " > $AWS_CLI/aws/credentials
export AWS_CONFIG_FILE=$AWS_CLI/aws/credentials
LOCAL_DIR="$AWS_CLI/data"

for file in $LOCAL_DIR/*; do
    aws s3 cp"$file" s3://$s3_bucket/$file
done