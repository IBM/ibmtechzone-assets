import dask.dataframe as dd
ACCESS_KEY = os.environ["access_key"]
SECRET_KEY = os.environ["secret_key"]
BUCKET_NAME = os.environ["bucket_name"]
S3_ENDPOINT = os.environ["s3_endpoint"]

s3_options = {
    'key': ACCESS_KEY,
    'secret': SECRET_KEY,
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT
    }
}
df = dd.read_csv('s3://'+BUCKET_NAME+'/*.csv', storage_options=s3_options)
df.compute().to_csv('combined.csv', index=False)