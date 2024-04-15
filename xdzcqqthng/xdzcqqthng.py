import os
import sqlite3
import boto3
from botocore.exceptions import NoCredentialsError
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

# AWS credentials
aws_access_key_id = os.environ["aws_access_key_id"]
aws_secret_access_key = os.environ["aws_secret_access_key"]
aws_bucket_name = os.environ["aws_bucket_name"]
aws_file_key = os.environ["aws_file_key"]

# SQLite database setup
db_filename = 'local_db.sqlite' #give any name your choice for DB
table_name = 'data_table'

if os.path.exists(db_filename):
    os.remove(db_filename)

engine = create_engine(f'sqlite:///{db_filename}', echo=True)
metadata = MetaData()
data_table = Table(table_name, metadata,
                   Column('ID', Integer, primary_key=True),
                   Column('Gender', String),
                   Column('Age', Integer),
                   Column('Experience', Integer),
                   Column('Current_Salary', Integer),
                   Column('score', Integer)
                   )

metadata.create_all(engine)

# AWS S3 download and data insertion into SQLite
try:
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    s3.download_file(aws_bucket_name, aws_file_key, 'downloaded_file.csv')

    conn = engine.connect()
    with open('downloaded_file.csv', 'r') as file:
        next(file)  # Skip header if needed
        for line in file:
            columns = line.strip().split(',')  # Assuming CSV format
            conn.execute(data_table.insert().values(Gender=columns[0], Age=columns[1], Experience=columns[2], Current_Salary=columns[3], score=columns[4]))  # Insert data
    conn.close()

    print("Data transfer successful.")

except NoCredentialsError:
    print("AWS credentials not available.")
except Exception as e:
    print(f"Error occurred: {str(e)}")