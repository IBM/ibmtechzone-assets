import os
import snowflake.connector
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import pandas as pd
import io
import csv

# Constants for IBM COS values
COS_ENDPOINT = os.environ.get("COS_ENDPOINT")
COS_API_KEY_ID = os.environ.get("COS_API_KEY_ID")
COS_INSTANCE_CRN = os.environ.get("COS_INSTANCE_CRN")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# Snowflake connection parameters
snowflake_account = os.environ.get("SNOWFLAKE_ACCOUNT")
snowflake_user = os.environ.get("SNOWFLAKE_USER")
snowflake_password = os.environ.get("SNOWFLAKE_PASSWORD")
snowflake_database = os.environ.get("SNOWFLAKE_DATABASE")
snowflake_schema = os.environ.get("SNOWFLAKE_SCHEMA")
snowflake_warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE")
snowflake_table = os.environ.get("SNOWFLAKE_TABLE")
# Connect to Snowflake
conn = snowflake.connector.connect(
    user=snowflake_user,
    password=snowflake_password,
    account=snowflake_account,
    database=snowflake_database,
    schema=snowflake_schema,
    warehouse=snowflake_warehouse
)

def fetch_data_from_snowflake(table_name, limit=10):
    # Fetch data from Snowflake
    query = f'SELECT * FROM {table_name} LIMIT {limit}'
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    return results

# Example usage
table_name = snowflake_table  # You can change this to any table name you want
results = fetch_data_from_snowflake(table_name)

# Convert Snowflake results to DataFrame
df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

# IBM COS connection parameters
cos_config = {
    'endpoint': COS_ENDPOINT,
    'ibm_api_key_id': COS_API_KEY_ID,
    'ibm_service_instance_id': COS_INSTANCE_CRN,
    'config': Config(signature_version='oauth'),
    'bucket': BUCKET_NAME
}

# Create a CSV string from the data
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_content = csv_buffer.getvalue()

# Close the CSV buffer
csv_buffer.close()

# Upload the CSV content to IBM COS
cos.put_object(Bucket=cos_config['bucket'], Key=f'{table_name}_data.csv', Body=csv_content.encode('utf-8'))
