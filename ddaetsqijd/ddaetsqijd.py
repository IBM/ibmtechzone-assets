import os
from pymilvus import Collection, connections
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from app.prompts import promptv2
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
import json
import time

load_dotenv()

project_id = os.getenv("PROJECT_ID")

def get_credentials():
    url = os.getenv("EMBEDDING_URL")
    apikey = os.getenv("API_KEY")
    
    if not url or not apikey:
        raise ValueError("EMBEDDING_URL and API_KEY environment variables must be set.")
    
    return {"url": url, "apikey": apikey}

def create_model(max_tokens=2000):
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": max_tokens,
        "min_new_tokens": 1,
        "stop_sequences": ["<end>"],
    }
    if not project_id:
        raise ValueError("PROJECT_ID environment variable must be set.")

    return Model(
        model_id='mistralai/mixtral-8x7b-instruct-v01',
        params=parameters,
        credentials=get_credentials(),
        project_id=project_id
    )

def create_input_data(column_list, data):
    if not isinstance(data, pd.DataFrame):
        raise TypeError("The 'data' parameter must be a pandas DataFrame.")
    
    if not set(column_list).issubset(data.columns):
        raise ValueError("One or more columns in 'column_list' are not present in 'data'.")
    
    return json.dumps({column: ', '.join(data[column].astype(str)) for column in column_list}, ensure_ascii=False)

def prompt_and_model(prompt_text, max_tokens):
    model = create_model(max_tokens)
    
    try:
        response = model.generate(prompt=prompt_text)
    except Exception as e:
        raise RuntimeError("Model generation failed.") from e
    
    final_response = response.get("results", [{}])[0].get("generated_text", "")
    for marker in ["### 出力:", "### 回答:", "出力要約:", "要約:"]:
        marker_position = final_response.find(marker)
        if marker_position != -1:
            return final_response[marker_position + len(marker):].strip()
    return final_response

def search_collection(collection_name: str, query_embedding: List[float], top_k: int, similarity_threshold: float):
    collection = Collection(collection_name)
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["index", "metadata", "text"],
        consistency_level="Eventually"
    )
    
    filtered_results = []
    for hits in results:
        for hit in hits:
            similarity = hit.distance
            if similarity > similarity_threshold:
                filtered_results.append({
                    "ID": str(hit.entity.get('index')),
                    "Similarity Score": str(similarity),
                    "Metadata": hit.entity.get('metadata'),
                    "Text": hit.entity.get('text'),
                    "Collection": collection_name
                })
    
    return filtered_results

def parallel_milvus_extraction_and_summarize(query_embedding: List[float], top_k: int = 10, similarity_threshold: float = 0.8):
    # Milvus connection parameters
    MILVUS_HOST = os.getenv("MILVUS_HOST")
    MILVUS_PORT = os.getenv("MILVUS_PORT")
    COLLECTION_NAMES = os.getenv("MILVUS_COLLECTION_NAMES").split(",")

    if len(COLLECTION_NAMES) != 3:
        raise ValueError("Exactly three collection names must be provided in MILVUS_COLLECTION_NAMES environment variable.")

    # Connect to Milvus
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

    # Search all collections in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        search_results = list(executor.map(
            lambda name: search_collection(name, query_embedding, top_k, similarity_threshold),
            COLLECTION_NAMES
        ))

    # Flatten the results
    all_results = [item for sublist in search_results for item in sublist]

    # Convert results to DataFrame
    df = pd.DataFrame(all_results)

    # Close Milvus connection
    connections.disconnect(alias='default')

    # Prepare data for summarization
    claim_columns = ['column1','column2']
    proposed_solution_columns = ['column3','column4']
    preventive_measure_columns = ['column5','column6']

    claim_data = create_input_data(claim_columns, df.iloc[[0]])
    proposed_solution_data = create_input_data(proposed_solution_columns, df.head(10))
    preventive_measure_data = create_input_data(preventive_measure_columns, df.head(10))

    prompts = (
        promptv2.prompt_claim_summary.format(text=claim_data),
        promptv2.prompt_previous_action_summary.format(text=proposed_solution_data),
        promptv2.prompt_future_action_summary.format(text=preventive_measure_data)
    )

    max_tokens_claim = 200
    max_tokens_others = 2000

    start = time.time()
    with ThreadPoolExecutor(max_workers=3) as executor:
        output = list(executor.map(
            lambda p_and_t: prompt_and_model(*p_and_t), 
            zip(prompts, [max_tokens_claim, max_tokens_others, max_tokens_others])
        ))
    end = time.time()

    print("execution time", end - start)

    return {
        "extracted_data": df.to_dict(orient='records'),
        "summaries": {
            "claim_summary": output[0],
            "proposed_solution_summary": output[1],
            "preventive_measure_summary": output[2]
        }
    }

# Example usage:
# query_embedding = ... # Your query embedding here
# result = parallel_milvus_extraction_and_summarize(query_embedding)
# print(result)