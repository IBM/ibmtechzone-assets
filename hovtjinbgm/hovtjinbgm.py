import prestodb
import pandas as pd
import os
from pyspark.sql import SparkSession

#Read data from WatsonX.data using prestodb
host_name = os.environ["host_name"]
port = os.environ["port"]
username = os.environ["username"]
password = os.environ["password"]
catalog_name = os.environ["catalog_name"]
schema_name = os.environ["schema_name"]
sql_query = os.environ["sql_query"]
aws_access_key_id = os.environ["aws_access_key_id"]
aws_secret_access_key = os.environ["aws_secret_access_key"]
s3_bucket_path = os.environ["s3_bucket_path"]

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

query = sql_query
df = pd.read_sql_query(query, conn)


# Create SparkSession
spark = SparkSession.builder \
    .appName("minio_to_s3") \
    .getOrCreate()

df_spark = spark.createDataFrame(df)

# AWS credentials and S3 bucket path
aws_access_key_id = aws_access_key_id
aws_secret_access_key = aws_secret_access_key


# Set AWS credentials
spark.sparkContext._jsc.hadoopConfiguration().set('fs.s3a.access.key', aws_access_key_id)
spark.sparkContext._jsc.hadoopConfiguration().set('fs.s3a.secret.key', aws_secret_access_key)

df_spark.write.mode("overwrite").csv((s3_bucket_path))