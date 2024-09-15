from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import logging
from pymilvus import connections, Collection
import prestodb
from ibm_watsonx_ai.foundation_models import Model
import pandas as pd
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables for environment configuration
host = os.getenv("MILVUS_HOST", None)
port = os.getenv("MILVUS_PORT", None)
password = os.getenv("MILVUS_PASSWORD", None)
user = os.getenv("MILVUS_USER_NAME", None)
server_pem_path = os.getenv("MILVUS_CERTIFICATE_PATH", None)
catalog = os.getenv("CURRENT_CATALOG", None)
schema = os.getenv("CURRENT_SCHEMA", None)
model_id = os.getenv("LLM_MODEL_ID", None)

parameters = {
    "decoding_method": os.getenv("DECODING_METHOD", None),
    "max_new_tokens": int(os.getenv("MAX_NEW_TOKEN", None)),
    "repetition_penalty": float(os.getenv("REPETITION_PENALTY", None))
}

project_id = os.getenv("PROJECT_ID", None)

# Initialize the model using IBM Watson LLM
model = Model(
    model_id=model_id,
    params=parameters,
    credentials={"url": os.getenv("CLOUD_URL", None), "apikey": os.getenv("API_KEY", None)},
    project_id=project_id
)
table_dict={}
# Route 1: Fetch metadata from wx.data (PrestoDB)
@app.get("/fetch-metadata/")
async def fetch_metadata():
    try:
        # Connect to PrestoDB and fetch table names
        cursor = connect_presto()
        tables = fetch_tables(catalog, schema, cursor)
        for table in tables:
            table_name = table[0]
            columns = fetch_columns(catalog, schema, table_name, curr)
            table_dict[table_name] = columns
        return {"tables": table_dict}
    except Exception as e:
        logging.error(f"Error fetching metadata: {e}")
        raise HTTPException(status_code=500, detail="Error fetching metadata")

# Route 2: Enrich metadata using LLM
@app.post("/enrich-metadata/")
async def enrich_metadata(data: dict):
    try:
        json_output = {}
        for table, columns_data in table_dict.items():
            json_output[table] = generate_metadata(table, columns_data)
        json_output_str = json.dumps(json_output).replace("\\n", "")

    # Parse and print the JSON output
        for key in json_output:
            if isinstance(json_output[key], str):
                logging.info(f"Parsing JSON for key: {key}")
                json_output[key] = json.loads(json_output[key])
        json_output_str = json.dumps(json_output, indent=4)
        logging.info("Data fetch and store process completed.")
        return json_output_str
    except Exception as e:
        logging.error(f"Error enriching metadata: {e}")
        raise HTTPException(status_code=500, detail="Error enriching metadata")

# Route 3: Store enriched data in Milvus
@app.post("/store-metadata/")
async def store_metadata(data: dict):
    try:
        # Connect to Milvus
        connections.connect(
            alias='default',
            host=host,
            port=port,
            user=user,
            password=password,
            server_pem_path=server_pem_path,
            secure=True
        )
        
        store_metadata = create_milvus_collection()


        return {"message": "Enriched metadata stored in Milvus successfully"}
    except Exception as e:
        logging.error(f"Error storing metadata in Milvus: {e}")
        raise HTTPException(status_code=500, detail="Error storing metadata")

# Helper Functions
def connect_presto():
    # Connect to PrestoDB
    prestoconn = prestodb.dbapi.connect(
        host=os.getenv("PRESTO_DB_HOST", None),
        port=int(os.getenv("PRESTO_DB_PORT_NUMBER", None)),
        user=os.getenv("PRESTO_DB_USER_NAME", None),
        catalog=os.getenv("PRESTO_DB_CATALOG", None),
        schema=os.getenv("PRESTO_DB_SCHEMA", None),
        http_scheme=os.getenv("PRESTO_DB_HTTP_SCHEMA", None),
        auth=prestodb.auth.BasicAuthentication(os.getenv("PRESTO_DB_USER_NAME", None), os.getenv("PRESTO_DB_PASSWORD", None))
    )
    prestoconn._http_session.verify = os.getenv("PRESTO_DB_CERTIFICATE_PATH", None)
    logging.info("Connected to PrestoDB.")
    return prestoconn.cursor()

def fetch_tables(catalog, schema, conn):
    sql = f"SHOW tables from {catalog}.{schema}"
    conn.execute(sql)
    table_names = conn.fetchall()
    logging.info(f"Fetched tables: {table_names}")
    return table_names

def generate_metadata(table_name, columns_data):
    # Generate metadata using LLM
    prompt_input = f"Generate metadata in JSON for the table: {table_name}, with columns data: {columns_data}"
    response = model.generate_text(prompt=prompt_input)
    return json.loads(response)

def create_milvus_collection():
    # Create Milvus collection for storing metadata vectors
    logging.info("Storing data in Milvus.")
    connections.connect(
        alias='default',
        host=host,
        port=port,
        user=user,
        password=password,
        server_pem_path=server_pem_path,
        server_name='watsonxdata',
        secure=True
    )

    collection_name = "data_collection"

    # Define schema for Milvus collection
    fields = [
        FieldSchema(name="tableName", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="tableDescription", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="columnName", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="dataType", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="exampleValue", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),
    ]
    schema = CollectionSchema(fields, "Hive Data Ontime")

    # Create Milvus collection
    data_collection = Collection(collection_name, schema)

    # Create index for the collection
    index_params = {
        'metric_type': 'L2',
        'index_type': "IVF_FLAT",
        'params': {"nlist": 2048}
    }
    data_collection.create_index(field_name="vector", index_params=index_params)

    # Initialize sentence transformer model for generating embeddings
    model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", None))

    # Generate vector embeddings for each record
    vector = data['vector'].tolist()
    vector_embeddings = model.encode(vector).tolist()

    # Prepare records for insertion
    records = [
        {
            "tableName": str(row['tableName']),
            "tableDescription": str(row['tableDescription']),
            "columnName": str(row['columnName']),
            "description": str(row['description']),
            "dataType": str(row['dataType']),
            "exampleValue": str(row['exampleValue']),
            "vector": vector_embeddings[i]
        }
        for i, row in data.iterrows()
    ]

    # Insert data into Milvus collection and load it
    data_collection.insert(records)
    data_collection.flush()
    data_collection.load()

    logging.info("Data loaded into Milvus successfully.")

def dict_to_df(data):
    # Convert JSON metadata into a pandas DataFrame
    table_list = []
    for key, value in data.items():
        parsed_value = value if isinstance(value, dict) else json.loads(value)
        for table in parsed_value['tables']:
            table_name = table['tableName']
            table_description = table['description']
            for column in table['columns']:
                table_list.append({
                    'tableName': table_name,
                    'tableDescription': table_description,
                    'columnName': column['columnName'],
                    'description': column['description'],
                    'dataType': column['dataType'],
                    'exampleValue': column['exampleValue']
                })

    df = pd.DataFrame(table_list)

    # Define new column order for the DataFrame
    new_column_order = ['tableName', 'tableDescription', 'columnName', 'description', 'dataType', 'exampleValue']
    df = df[new_column_order]

    # Generate vector representation for each row
    df['vector'] = df.apply(lambda row: f"'tableName':{row['tableName']},'tableDescription': {row['tableDescription']},'columnName': {row['columnName']},'column description' :{row['description']},'dataType': {row['dataType']}", axis=1)
    logging.info("Converted JSON metadata to DataFrame.")
    return df


