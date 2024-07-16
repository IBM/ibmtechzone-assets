from dotenv import load_dotenv
import os, ast, re
import pandas as pd
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from utils.milvus import VectorDB
from utils.reranking2 import custom_reranker
from utils.query_expansion_jpn import Generate_joint_query
from config import COLLECTION_NAME

Top_K = 5
vectordb = VectorDB()
load_dotenv()
api_key = os.getenv("IBM_CLOUD_API_KEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("PROJECT_ID", None)


def get_doc_info(relevant_chunks):
    doc_information = []
    for hits in relevant_chunks:
        for hit in hits:
            doc_information.append({'distance': hit.distance, 'chunk_id': hit.get('chunk_id'),
                                    'chunk': str(hit.get('chunks')).replace(" ", ""), 'url': hit.get('url')})
    sorted_doc_info = sorted(doc_information, key=lambda x: x['distance'], reverse=True)

    return sorted_doc_info


def get_wml_creds():
    if api_key is None or ibm_cloud_url is None or project_id is None:
        print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
    else:
        creds = {
            "url": ibm_cloud_url,
            "apikey": api_key
        }
    return project_id, creds


project_id, creds = get_wml_creds()


def calling_watsonx(prompt):
    params = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.MAX_NEW_TOKENS: 500,
        GenParams.TEMPERATURE: 0,
    }
    model = Model(model_id='meta-llama/llama-3-70b-instruct', params=params, credentials=creds, project_id=project_id)
    response = model.generate_text(prompt)
    return response


def make_clickable(val):
    return f'<a href="{val}" target="_blank">{val}</a>'


def display_df(df):
    return df.to_html(escape=False)


def get_chunks(question_text, default_flag=False, collection_name=COLLECTION_NAME, doc_flag=False):
    new_sorted_chunks = []
    relevant_chunks = vectordb.query_milvus(question_text, collection_name)
    doc_information = get_doc_info(relevant_chunks)
    # new_sorted_chunks = custom_reranker(question_text, doc_information)
    reference_df = pd.DataFrame(doc_information)
    reference_df = reference_df.rename(columns={"distance": "score"})
    reference_df.drop("chunk_id", axis=1, inplace=True)

    if not doc_flag:
        return reference_df, not default_flag
    return doc_information


def make_prompt(question_text, doc_information):
    retrieved_data = ""
    for index, i in enumerate(doc_information):
        retrieved_data += (f"[{index + 1}] " + f"{i['chunk']}" + "\n")
    retrieved_data = retrieved_data.replace("}", "")
    retrieved_data = retrieved_data.replace("{", "")
    prompt = f"""system
Please answer in Japanese. Please read the following documents and question. Each document is not directly related, so please do not confuse them. If there is relevant information, please answer in detail based on that document. When writing your answer, please use words from the documents as much as possible. In other words, prioritize words from the documents when selecting them. If the answer to the question is not clearly stated in the document, please answer, "The answer to the question is not clearly stated in the document." You are a kind, polite, and sincere assistant. Please provide detailed answers while ensuring safety and supporting the user as much as possible. Please do not include harmful, unethical, racially discriminatory, sexist, toxic, dangerous, or illegal content in your answers. Please ensure that your answers are socially unbiased and fundamentally positive. If the question does not make sense or contradicts facts, please explain the reason rather than providing incorrect information. If you do not know the answer to the question, please do not share incorrect information.
At the end of your answer, please cite the source of information in the format of [1] (Example: XXX.([1])). List the document number (e.g., [1]) and title at the end of the answer, citing only the documents used in creating the answer under "References". List them in the format XXX. List the document number(s) relevant to the answer; do not list documents that are not relevant.

Steps:

1. When creating an answer, please follow the sample answer format below. Cite documents only as "References" at the end of the answer.

Sample Answer Format:

"Answer to the question"
References: [Number]

2. In addition to quoting documents, include appropriate explanations for each quoted reference in the answer.


User
<document>
{retrieved_data}
</document>
<question> {question_text} </question>
AssistantJapanese response:""".format(question_text=question_text, retrieved_data=retrieved_data)
    return prompt, doc_information
