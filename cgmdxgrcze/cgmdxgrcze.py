from minio import Minio
import prestodb
from io import BytesIO
import numpy as np
import pandas as pd

def pandas_to_presto_type(pandas_type):
    """
    Converts a Pandas data type to the corresponding Presto SQL data type.

    Parameters:
    - pandas_type (type): The Pandas data type to be converted.

    Returns:
    - str: The corresponding Presto SQL data type.

    Examples:
    >>> pandas_to_presto_type(int)
    'BIGINT'
    >>> pandas_to_presto_type(float)
    'DOUBLE'
    >>> pandas_to_presto_type(bool)
    'BOOLEAN'
    >>> pandas_to_presto_type(pd.Timestamp)
    'TIMESTAMP'
    >>> pandas_to_presto_type(pd.Timedelta)
    'VARCHAR'
    """
    if issubclass(pandas_type, (np.integer, np.int64, np.int32)):
        return 'BIGINT'
    elif issubclass(pandas_type, (np.floating, np.float64, np.float32)):
        return 'DOUBLE'
    elif issubclass(pandas_type, np.bool_):
        return 'BOOLEAN'
    elif issubclass(pandas_type, (np.datetime64, pd.Timestamp)):
        return 'TIMESTAMP'
    elif issubclass(pandas_type, (np.timedelta64, pd.Timedelta)):
        return 'VARCHAR'
    else:
        return 'VARCHAR'
    
def create_minio_client():
    """
    Create and return a MinIO client object configured with the provided credentials.

    Returns:
    - Minio: A MinIO client object configured with the provided credentials.

    Notes:
    - The MinIO client is initialized with the endpoint, access key, and secret key.
    - The `secure` parameter is set to False to allow connection without SSL/TLS encryption.
    """
    minio_client = Minio(
        endpoint='**********',
        access_key='************',
        secret_key='****************',
        secure=False
    )

    return minio_client

def connect_PrestoDB(dbHost='na4.services.cloud.techzone.ibm.com',
                     dbPort=48931,
                     dbUser='ibmlhadmin',
                     dbCatalog='tpch',
                     dbSchema='tiny',
                     dbHttp_scheme='https',
                     dbCert = 'lh-ssl-ts-2.crt'):
     """
    Establish a connection to PrestoDB and return a cursor object for executing queries.

    Parameters:
    - dbHost (str): The hostname or IP address of the PrestoDB server. Default is 'na4.services.cloud.techzone.ibm.com'.
    - dbPort (int): The port number of the PrestoDB server. Default is 48931.
    - dbUser (str): The username for authentication. Default is 'ibmlhadmin'.
    - dbCatalog (str): The catalog to use. Default is 'tpch'.
    - dbSchema (str): The schema to use. Default is 'tiny'.
    - dbHttp_scheme (str): The HTTP scheme to use ('http' or 'https'). Default is 'https'.
    - dbCert (str): The path to the SSL certificate file for verifying the server's SSL certificate.
                    Default is 'lh-ssl-ts-2.crt'.

    Returns:
    - Cursor: A cursor object for executing queries on the PrestoDB connection.

    Notes:
    - This function establishes a connection to PrestoDB using the provided parameters and returns a cursor object.
    - The default values are provided for typical usage, but they can be overridden as needed.
    """
     prestoconn = prestodb.dbapi.connect(
         host=dbHost,
         port=dbPort,
         user=dbUser,
         catalog=dbCatalog,
         schema=dbSchema,
         http_scheme=dbHttp_scheme,
         auth=prestodb.auth.BasicAuthentication("ibmlhadmin", "password")
         )
     prestoconn._http_session.verify = dbCert
     curr = prestoconn.cursor()
     return curr

def create_sql_schema(schema, table_name):
    """
    Generate SQL to create a schema in Hive.

    Parameters:
    - schema (str): The name of the schema to create.
    - table_name (str): The name of the table associated with the schema (not used in this function).

    Returns:
    - str: The SQL statement to create the schema in Hive.

    Notes:
    - This function generates an SQL statement to create a schema in Hive.
    - The schema will be created under the 'hive_data' catalog and its location will be set to an S3 bucket path.
    """
    generatedSQL = f"""create schema hive_data.{schema} with (location = 's3a://hive-bucket/{schema}')"""

    return generatedSQL

def create_sql_table(schema, table_name, column_dict):
    """
    Generate SQL to create a table in Hive.

    Parameters:
    - schema (str): The name of the schema where the table will be created.
    - table_name (str): The name of the table to create.
    - column_dict (dict): A dictionary mapping column names to their respective data types.

    Returns:
    - str: The SQL statement to create the table in Hive.

    Notes:
    - This function generates an SQL statement to create a table in Hive.
    - The table will be created under the specified schema in the 'hive_data' catalog.
    - The table's columns and data types are defined by the provided column_dict.
    - The table will be stored in CSV format and its location will be set to an S3 bucket path.
    """
    
    sql_query = f"CREATE TABLE hive_data.{schema}.{table_name} ("

    
    for col_name, data_type in column_dict.items():
        sql_query += f"{col_name} {data_type}, "

    sql_query = sql_query.rstrip(', ') + f""") WITH (format = 'CSV', external_location='s3a://hive-bucket/{schema}/{table_name}')"""

    return sql_query

def create_hive_tables(schema, table_name, presto_data_types):
    """
    Create a schema and table in Hive using Presto.

    Parameters:
    - schema (str): The name of the schema to create.
    - table_name (str): The name of the table to create.
    - presto_data_types (dict): A dictionary mapping column names to Presto data types.

    Returns:
    - tuple: A tuple containing the results of creating the schema and table.

    Notes:
    - This function connects to a Presto database and creates a schema and table.
    - The schema will be created first using the specified name.
    - The table will be created under the specified schema with the given name and column data types.
    - If the schema or table creation fails, the corresponding error message will be returned in the result tuple.
    """
    conn = connect_PrestoDB()
    SQL_schema = create_sql_schema(schema, table_name)
    try:
        res1 = conn.execute(SQL_schema)
    except Exception as e:
        res1 = e
    try:
        SQL_table = create_sql_table(schema, table_name, presto_data_types)
        res2 = conn.execute(SQL_table)
    except Exception as e:
        res2 = e
    return res1, res2

def read_hive_tables_name(schema: str) -> list[str]:
    """
    Retrieve the names of tables in a schema from Minio.

    Parameters:
    - schema (str): The name of the schema containing the tables.

    Returns:
    - list[str]: A list of table names in the specified schema.

    Notes:
    - This function connects to Minio and retrieves the list of objects (table names) under the specified schema.
    - The schema name is used as the prefix when listing objects.
    - The object names correspond to the table names in the schema.
    """
    minio_client = create_minio_client()
    objects = minio_client.list_objects(
            bucket_name='hive-bucket',
            prefix=schema,
            recursive=True
        )
    files = []
    for obj in objects:
        files.append(obj.object_name)
    return files    

def load_data_hive(bucket_name, file):
    """
    Load data from a CSV file stored in Minio.

    Parameters:
    - bucket_name (str): The name of the Minio bucket containing the CSV file.
    - file (str): The name of the CSV file to load.

    Returns:
    - pd.DataFrame: A DataFrame containing the data from the CSV file.

    Notes:
    - This function retrieves the specified CSV file from the Minio bucket and loads it into a DataFrame.
    - The CSV file is assumed to be stored in the specified bucket.
    - The file parameter should include the path if the file is stored in a subdirectory within the bucket.
    """

    minio_client = create_minio_client()
    data = minio_client.get_object(bucket_name, file)
    csv_data = data.read()
    return pd.read_csv(BytesIO(csv_data), dtype=object)

def create_hive_tables(bucket_name, project_name):
    """
    Create Hive tables based on CSV files stored in a Minio bucket.

    Parameters:
    - bucket_name (str): The name of the Minio bucket containing the CSV files.
    - project_name (str): The name of the project or schema under which the tables will be created.

    Returns:
    - None

    Notes:
    - This function retrieves the list of CSV files stored in the specified Minio bucket.
    - It then loads each CSV file into a DataFrame and determines the appropriate Presto data types for each column.
    - Finally, it creates Hive tables in the specified project or schema using the determined column names and data types.
    """
    minio_client = create_minio_client()
    schema = project_name
    schema = schema.replace(' ', '_')
    schema = schema.replace('-', '_')
    files = read_hive_tables_name('hive-bucket', schema)
    for file in files:
        df = load_data_hive(bucket_name, file)
        table_name = file.split('/')[1]
        presto_data_types = {col: pandas_to_presto_type(df[col].dtype.type) for col in df.columns}
        res1, res2 = create_hive_tables(schema, table_name, presto_data_types)

if __name__ == '__main__':
    bucket_name = str(input('Enter bucket name in Minio: '))
    project_name = str(input('Enter project folder name: '))
    create_hive_tables(bucket_name, project_name)