from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import ibm_boto3
import json

app = FastAPI()

def generate_url_for_object(cos_access_key_id: str, cos_secret_access_key: str, cos_endpoint_url: str,expiration: int, key_name: str, bucket_name: str):
    try:
        cos_client = ibm_boto3.client(
            service_name="s3",
            aws_access_key_id=cos_access_key_id,
            aws_secret_access_key=cos_secret_access_key,
            endpoint_url=cos_endpoint_url
        )

        http_method = 'get_object'
        expiration = expiration             
        signedUrl = cos_client.generate_presigned_url(http_method, Params={'Bucket': bucket_name, 'Key': key_name}, ExpiresIn=expiration)
        return signedUrl
    except Exception as e:
        print(f"An error occurred while creating the url: {e}")
        return None

@app.get("/generate-url/")
async def generate_presigned_url(cos_access_key_id: str,cos_secret_access_key: str,cos_endpoint_url: str,expiration: int,key_name: str, bucket_name: str):
    return {"presignedurl" : generate_url_for_object(cos_access_key_id, cos_secret_access_key, cos_endpoint_url, expiration,key_name, bucket_name)}