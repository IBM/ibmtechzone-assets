###### Function for ELastic search SQL table
import pandas as pd
from elasticsearch import Elasticsearch, AsyncElasticsearch
from langchain.text_splitter import CharacterTextSplitter
from elasticsearch.helpers import scan, bulk
import pandas as pd
from langchain.vectorstores.elasticsearch import ElasticsearchStore
import copy
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from dotenv import load_dotenv
from langchain.chains import RetrievalQA

load_dotenv()
# Define your Elasticsearch settings
elasticsearch_url = os.getenv("elasticsearch_url", None)
username = os.getenv("username", None)
password = os.getenv("password", None)
index_name = ''
cert_path = '1fa4c2a5-03a2-4559-abec-9c6ef81bd506.crt'

wx_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("PROJECT_ID", None)
wx_api=os.getenv("API_KEY", None)

es_connection = Elasticsearch(
    elasticsearch_url,
    ca_certs=cert_path,
    basic_auth=(username, password)
)


dest_index_name = 'embed-index_web_test1'
es_model_id=".elser_model_1"


######## SQL QUERY
res1=es_connection.sql.query(pretty=True,body={'query':"""SELECT * FROM "new_test" where BloodPressure < 80 limit 5 """})
columns=res1['columns']
rows=res1['rows']
df = pd.DataFrame(rows, columns=[col['name'] for col in columns])
print(df)