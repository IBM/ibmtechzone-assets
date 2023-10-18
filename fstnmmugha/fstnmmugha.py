import dask.dataframe as dd
ACCESS_KEY = os.environ["access_key"]
SECRET_KEY = os.environ["secret_key"]
BUCKET_NAME = os.environ["bucket_name"]

df = dd.read_csv('s3://'+BUCKET_NAME+'/*.csv', storage_options={'key': ACCESS_KEY, 'secret': SECRET_KEY})
df.compute().to_csv('combined.csv', index=False)