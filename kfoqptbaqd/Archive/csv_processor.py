import pandas as pd
import numpy as np
from io import StringIO
from llm_answer_generator import generate_llm_answers
from llm_evaluation import llm_evaluation
from embedding_similarity import calculate_similarity
from entity_extraction import extract_numerical_entities, compare_entities
import asyncio

from request_custom_rag import get_rag_responses
#from numerical_review import check_non_null

class ProcessingError(Exception):
    """Custom exception class for processing errors."""
    pass

def process_csv(file, api_key='', url='', env_id='', watsonai_apikey='', ibm_cloud_url='', project_id='', ip='127.0.0.1', port=5000, rag_type = 'assistant'):
    try:
        df = pd.read_csv(file)
        # Ensure 'question' column exists
        if 'question' not in df.columns:
            raise ProcessingError("Column 'question' not found in CSV")

    except Exception as e:
        raise ProcessingError(f"Error reading CSV file: {e}")

    try:
        questions = df['question'].tolist()
        expected_answers = df['expected answer'].tolist()

        if rag_type == 'assistant':
            print('running for assistant')
            llm_answers = asyncio.run(generate_llm_answers(questions, api_key, url, env_id))
        elif rag_type == 'custom':
            print('running for custom rag')
            llm_answers = asyncio.run(get_rag_responses(questions, ip, port))

        df['llm generated answer'] = llm_answers
       

    except Exception as e:
        raise ProcessingError(f"Error in LLM answer generation: {e}")

    try:
        similarity_scores = calculate_similarity(expected_answers, llm_answers)
        df['similarity score'] = similarity_scores
        df['similarity score'] = df['similarity score'].round(2)

        expected_entities = extract_numerical_entities(expected_answers)
        llm_entities = extract_numerical_entities(llm_answers)
        df['numerical entities expected'] = expected_entities
        df['numerical entities llm'] = llm_entities

        LLM_based_eval = asyncio.run(llm_evaluation(watsonai_apikey, ibm_cloud_url, project_id, questions, expected_answers, llm_answers))
        df['LLM based eval'] = LLM_based_eval

        # match_results = compare_entities(expected_entities, llm_entities)
        # df['entity match result'] = match_results
        #df['comments'] = df.apply(check_non_null, axis=1)
        #df['comments'] = np.where(pd.notnull(df['numerical entities expected']) or pd.notnull(df['numerical entities expected']), 1, 0)

    except Exception as e:
        raise ProcessingError(f"Error in processing data: {e}")

    # Return the CSV data as a string
    return df.to_csv(index=False)






