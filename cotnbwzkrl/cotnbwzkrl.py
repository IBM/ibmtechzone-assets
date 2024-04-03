aws_access_key_id = os.environ["aws_access_key_id"]
aws_secret_access_key = os.environ["aws_secret_access_key"]
aws_bucket_name = os.environ["aws_bucket_name"]
key_prefix = os.environ["key_prefix"] #enter key folder path in S3 where logs need to be stored
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime

class S3Handler(logging.Handler):
    def __init__(self, bucket_name, key_prefix, log_filename='log.txt'):
        super().__init__()
        self.bucket_name = bucket_name
        self.key_prefix = key_prefix
        self.log_filename = log_filename
        self.s3 = boto3.client('s3',
              aws_access_key_id=aws_access_key_id,
              aws_secret_access_key=aws_secret_access_key)

    def upload_to_s3(self, data):
        try:
            # Check if the log file exists in S3
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{self.key_prefix}/{self.log_filename}")
            if 'Contents' in response and len(response['Contents']) > 0:
                # Append mode: Get the current content and append new data
                existing_data = self.s3.get_object(Bucket=self.bucket_name, Key=f"{self.key_prefix}/{self.log_filename}")['Body'].read().decode()
                data = existing_data + "\n" + data.decode()

            self.s3.put_object(Body=data, Bucket=self.bucket_name, Key=f"{self.key_prefix}/{self.log_filename}")
        except NoCredentialsError:
            print("AWS credentials not found. Unable to upload logs to S3.")

    def format_record(self, record):
        timestamp = datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"{timestamp} - {record.process} - {record.levelname} - {record.message}"

    def emit(self, record):
        try:
            log_entry = self.format_record(record)
            self.upload_to_s3(log_entry.encode())
        except Exception as e:
            print(f"Error uploading log to S3: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(process)d-%(levelname)s-%(message)s')
logger = logging.getLogger()

# Add S3Handler to the logger
bucket_name = aws_bucket_name
key_prefix = key_prefix
s3_handler = S3Handler(bucket_name, key_prefix)
logger.addHandler(s3_handler)


try:
    logger.info("Logging info")
except Exception as e:
    logger.error('Error occurred ' + str(e))
    
#error block
try:
    prnt(ajdfnwelj)
except Exception as e:
    logger.error('Error occurred ' + str(e))