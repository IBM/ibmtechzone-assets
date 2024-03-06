export AWS_CLI="$(pwd)"
export PATH=$PATH:$AWS_CLI/aws/v2/current/bin
echo "AWS CLI has been installed here -> $AWS_CLI"
echo "[default]
aws_access_key_id = $s3_access_key
aws_secret_access_key = $s3_secret_key 
region = $s3_region 
endpoint_url = $s3_endpoint " > $AWS_CLI/aws/credentials
export AWS_CONFIG_FILE=$AWS_CLI/aws/credentials
aws s3 ls $s3_bucket --recursive