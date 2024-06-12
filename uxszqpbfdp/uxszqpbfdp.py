from minio import Minio
import pandas as pd
from io import BytesIO
import re

def create_minio_client():
    minio_client = Minio(
        endpoint='********',
        access_key='********',
        secret_key='***********',
        secure=False
    )

    return minio_client

def read_files_name(bucket_name: str, folder_path: str) -> dict:
    """
    Function to read all the csv files ih the given bucket and in a particular folder
    Arguments:
        bucket_name: name of the bucket
        folder_path: name of the folder within the bucket from where it will read all the csv files

    Output
        Returns the path of all the csv files
    
    """

    minio_client = create_minio_client()
    objects = minio_client.list_objects(
            bucket_name=bucket_name,
            prefix=folder_path,
            recursive=True
        )
    files = [obj.object_name for obj in objects if obj.object_name.endswith('.csv')]

    files_dict = {}
    for file in set([file.split('/')[1].split('-')[0] for file in files]):
        files_dict[file] = [x for x in files if file in x ]

    return files_dict

def load_data(bucket_name: str, files: str) -> dict:
    """
    Function to load the data from minio
    Arguments:
        bucket_name: name of the bucket
        files: list of file names to be loaded from minio bucket

    Output:
        Returns the dictionary where keys are file name and value is pandas dataframe

    """
    minio_client = create_minio_client()

    dfs = {}
    for file in files:
        data = minio_client.get_object(bucket_name, file)
        csv_data = data.read()
        dfs[file.split('/')[-1]] = pd.read_csv(BytesIO(csv_data), dtype=object)

    return dfs

def pre_processing(column_names):
    """
    Function to preprocess the column names
    Arguments:
        column_names: list of dataframe's column names

    Output:
        Returns the list of column names after removing special characters
    """
    regex_patterns = [
        (r'\n', ' '),  
        (r'\r', ' '),       
        (r'/', ' or '),     
        (r'[-().:]', ''), 
        (r'#', ' number ') 
    ]

    processed_column_names = column_names[:]
    for pattern, replacement in regex_patterns:
        processed_column_names = [re.sub(pattern, replacement, x) for x in processed_column_names]

    processed_column_names = [x.lower().strip() for x in processed_column_names] 
    processed_column_names = [x.replace(' ', '_') for x in processed_column_names] 
    processed_column_names = [re.sub(r'_+', '_', x) for x in processed_column_names]

    return processed_column_names

def create_hive_data(bucket_name: str, project_name: str):
    """
    Function to create csv files in hive bucket in minio
    Arguments:
        bucket_name: name of the bucket in minio
        project_name: name of the folder in the bucket

    Output:
        Create csv files in hive bucket in minio
    """
    minio_client = create_minio_client()
    schema = project_name
    schema = schema.replace(' ', '_')
    schema = schema.replace('-', '_')
    dict_mapping = {}
    files_dict = read_files_name(bucket_name, project_name)
    for key1, value1 in files_dict.items():
        dfs = load_data(bucket_name, files_dict[key1])
        for key, df in dfs.items():
            table_name = key.split('.csv')[0]
            table_name = re.sub(r'[-& ]+', '_', table_name)
            df.replace(to_replace=r'(?i)null', value='', regex=True, inplace=True)
            df.columns = pre_processing(df.columns)
            df = df.dropna(how='all').reset_index(drop=True)
            filepath = schema+'/'+table_name+'/'+table_name+'.csv'
            buffer = BytesIO()
            df.to_csv(buffer, header=False, index=False)
            buffer.seek(0)
            result = minio_client.put_object(bucket_name='hive-bucket', object_name=filepath, data=buffer, length=buffer.getbuffer().nbytes)

if __name__ == '__main__':
    bucket_name = str(input('Enter bucket name in Minio: '))
    project_name = str(input('Enter project folder name: '))
    create_hive_data(bucket_name, project_name)