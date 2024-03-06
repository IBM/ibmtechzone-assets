curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
export AWS_CLI="$(pwd)"
./aws/install -i $AWS_CLI/aws
echo "AWS CLI install location=$AWS_CLI"
export PATH=$PATH:$AWS_CLI/aws/v2/current/bin
aws --help