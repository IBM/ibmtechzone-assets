import dask.dataframe as dd
import os
ACCESS_KEY = os.environ["access_key"]
SECRET_KEY = os.environ["secret_key"]
BUCKET_NAME = os.environ["bucket_name"]
S3_ENDPOINT = os.environ["s3_endpoint"]
TARGET_BUCKET_NAME = os.environ["target_bucket_name"]

s3_options = {
    'key': ACCESS_KEY,
    'secret': SECRET_KEY,
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT
    }
}
df = dd.read_csv('s3://'+BUCKET_NAME+'/*.csv', storage_options=s3_options)
df.compute().to_csv('s3://'+TARGET_BUCKET_NAME+'/combined.csv', index=False)