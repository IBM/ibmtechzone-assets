#!/usr/bin/env python
# coding: utf-8

# Ingestion of table via Presto API

# In[1]:


import numpy as np
import pandas as pd

import os
#import presto
from sqlalchemy import create_engine, text
from pyiceberg.catalog import load_catalog


# In[6]:


pip install pyhive


# In[2]:


from pyhive import presto


# In[13]:


# Connection with Presto Engine
connect_args={'protocol':'https'}

host = "host.lakehouse.appdomain.cloud"
port = '31667'

username = 'ibmlhapikey'
password = 'password'
catalog = 'bdpf-catalog'
schema = 'schema_ingestion_test'

# create engine
engine = create_engine(f"presto://{username}:{password}@{host}:{port}/{catalog}/{schema}", connect_args=connect_args)
conn = engine.connect()


# In[14]:


sample_data=pd.DataFrame()
sample_data = pd.read_parquet('./dev-00001.parquet')
sample_data.to_sql("table_dev_00001_ingest", engine, schema=schema, index=False, if_exists='append')


# In[15]:


#View the ingested table on the database
sql = 'select * from bdpf_catalog.schema_ingestion_test.table_dev_00001_ingest limit 5'
df = pd.read_sql_query(text(sql),conn)
df


# In[25]:


sample_data.dtypes


# In[34]:


#sample_data['Occurrence_Time_Local','GPS_TimeStamp_Local'] = sample_data['Occurrence_Time_Local','GPS_TimeStamp_Local'].astype(Timestamp)
sample_data = sample_data.drop(['Occurrence_Time_Local','GPS_TimeStamp_Local'], axis =1)


# In[1]:


#sample_data.to_sql('table_dev_00002_ingest', engine, schema=schema, index=False, if_exists='append')


# In[18]:


from pyiceberg.catalog import load_catalog


# In[16]:


pip install pyiceberg


# Ingestion of table via S3 Filepath

# In[9]:


from dotenv import load_dotenv
import os
import s3fs

S3_REGION = 'Japan-Tokyo'
S3_ENDPOINT = 'https://s3.jp-tok.cloud-object-storage.appdomain.cloud' 
S3_ACCESS_KEY = 'accesskey'
S3_SECRET_KEY = 'secretkey'


# In[11]:


fs = s3fs.S3FileSystem(
    anon =False,
    use_ssl = True,
    client_kwargs = {
        "region_name" : S3_REGION,
        "endpoint_url" : S3_ENDPOINT,
        "aws_access_key_id" : S3_ACCESS_KEY,
        "aws_secret_access_key" : S3_SECRET_KEY,
        "verify" : True,
    })


# In[12]:


import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import Table
from io import BytesIO


# In[13]:


s3_filepath = "bdpf-jp-pre-poc-data01/medium/medium-00001.parquet"
pf = pq.ParquetDataset(s3_filepath, filesystem = fs)


# In[14]:


(pf.read_pandas()).to_pandas()


# In[15]:


s3_filepath = 's3://bdpf-jp-pre-poc-data01/medium'
s3_filepaths = [path for path in fs.ls(s3_filepath) 
                if path.endswith('.parquet')]
s3_filepaths


# In[ ]:


s3_filepath_data = 's3://bdpf-jp-pre-poc-data01/medium/medium-00001.parquet'
s3_filepaths = [path for path in fs.ls(s3_filepath) 
                if path.endswith('.parquet')]
s3_filepaths


# In[ ]:


#sample_data = 'bdpf-jp-pre-poc-data01/medium/medium-00001.parquet'
sample_data=pd.DataFrame()
sample_data = pd.read_parquet('./dev-00001.parquet')


# In[18]:


#for file in s3_filepaths:
    # Read Parquet file directly from S3
dataset = pq.ParquetDataset('bdpf-jp-pre-poc-data01/medium/medium-00016.parquet', filesystem=fs)
table = dataset.read().to_pandas()


# In[19]:


table.head()


# In[ ]:




