import os
os.system("pip3 install boto3")
import prestodb
import pandas as pd
from io import StringIO
import boto3

#Read data from WatsonX.data using prestodb
host_name = os.environ["host_name"]
port = 443
username = os.environ["username"]
password = os.environ["password"]
catalog_name = os.environ["catalog_name"]
schema_name = os.environ["schema_name"]
table_name = os.environ["table_name"]


aws_access_key_id = os.environ["aws_access_key_id"]
aws_secret_access_key = os.environ["aws_secret_access_key"]
bucket_name = os.environ["bucket_name"]
key = os.environ["key"]

#Create the connection to prestodb
conn=prestodb.dbapi.connect(
    host=host_name,
    port=port,
    user=username,
    password=password,
    http_scheme='https',
    auth=prestodb.auth.BasicAuthentication(username, password),
    catalog=catalog_name,
    schema=schema_name,
)
cur = conn.cursor()
sql_query = "select * from iceberg_data.iceberg_s3.{}".format(table_name)
query = sql_query
print(query)
df = pd.read_sql_query(query, conn)
print(df.head())



csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

# AWS credentials and S3 bucket path
aws_access_key_id = aws_access_key_id
aws_secret_access_key = aws_secret_access_key

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3.put_object(Bucket='wxdatatest',Key='asset_test.csv', Body=csv_buffer.getvalue())
response = s3.get_object(Bucket='wxdatatest', Key='asset_test.csv')
data = response['Body'].read().decode('utf-8')

# Read CSV data into a DataFrame
df = pd.read_csv(StringIO(data))

# Display DataFrame
print(df)