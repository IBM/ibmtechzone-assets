import ibm_boto3
from ibm_botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()

def generate_presigned_url_hmac(item_name, expiration=604800):
    # Initialize the COS client with HMAC credentials
    cos = ibm_boto3.client('s3',
                           aws_access_key_id=os.getenv("access_key_id"),
                           aws_secret_access_key=os.getenv("secret_access_key"),
                           config=Config(signature_version='s3v4'),
                           endpoint_url=os.getenv("endpoint_url"))

    try:
        # Generate the pre-signed URL
        presigned_url = cos.generate_presigned_url('get_object',
                                                   Params={'Bucket': os.getenv("bucket_name"), 'Key': item_name},
                                                   ExpiresIn=expiration)
        return presigned_url
    except Exception as e:
        print(f"Unable to generate pre-signed URL: {e}")
        return None
