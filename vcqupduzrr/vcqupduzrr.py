import re
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 100)
import os
import numpy as np
import getpass
import bs4
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from IPython.display import HTML


import os
wml_api_key = os.environ["wml_api_key"]
project_id = os.environ["project_id"]
wd_project_id = os.environ["wd_project_id"]
wd_url = os.environ["wd_url"]
wd_collection_id = os.environ["wd_collection_id"]
wd_api_key = os.environ["wd_api_key"]
wml_api_url="https://us-south.ml.cloud.ibm.com"

credentials = {
    "url": wml_api_url,
    "apikey": wml_api_key
}

from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
authenticator = IAMAuthenticator(wd_api_key)
discovery = DiscoveryV2(
    version='2020-08-30',
    authenticator=authenticator
)
discovery.set_service_url("https://api.us-south.discovery.watson.cloud.ibm.com/instances/44e82369-32c7-42ed-9629-832622260a42")
#https://us-south.discovery.watson.cloud.ibm.com/v2/instances/crn%3Av1%3Abluemix%3Apublic%3Adiscovery%3Aus-south%3Aa%2F9f8f95eee4714473a87fa319d964063c%3A44e82369-32c7-42ed-9629-832622260a42%3A%3A/projects/181bdb56-6576-42d1-ae55-524da8a01508/collections/1680af0d-6b24-0f51-0000-018c5aee3c6b/activity

dql_query = " "
flds = ["html", "extracted_metadata.filename", "document_id"]
response = discovery.query(
        project_id=wd_project_id,
        collection_ids=[wd_collection_id],
        query=dql_query,
        return_=flds,
    ).get_result()
doclist = discovery.list_documents(wd_project_id, wd_collection_id)
for doc in doclist.result['documents']:
    document = discovery.get_document(wd_project_id, wd_collection_id, doc['document_id'])
    doc['filename']=document.result['filename']
    doc['created'] = document.result['created']
existing_docs=doclist.result['documents']
file_names=['1_Why Digital Tokenization Is a Priority for the ETF Industry _ State Street.pdf','2_AI and the Future of Intelligent Investing _ State Street.pdf','3_Accelerating Data-Driven Investing _ State Street.pdf',
              '4_Five Questions Investors Should Be Asking About Outsourced Trading _ State Street.pdf','5_The Multi-Asset Era Demands a Public-Private Model_State Street.pdf']
doc_ids=[]
for i in range(5):
    list_all = [d for d in existing_docs if d['filename'] == file_names[i]]
    datetime=list_all[0]['created']
    if len(list_all)==1:
        smallest_index=0
    else:
        for x in range(1,len(list_all)):
            if list_all[x]['created']<datetime:
                datetime=list_all[x]['created']
                smallest_index=x
    doc_ids.append(list_all[smallest_index]['document_id'])
doc_ids


def get_model(model_type,max_tokens,min_tokens,decoding,temperature,repetition,random_seed):
    generate_params = {
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.MIN_NEW_TOKENS: min_tokens,
        GenParams.DECODING_METHOD: decoding,
        GenParams.TEMPERATURE: temperature,
        GenParams.REPETITION_PENALTY: repetition,
        GenParams.RANDOM_SEED: random_seed,
    }
    model = Model(
        model_id=model_type,
        params=generate_params,
        credentials=credentials,
        project_id=project_id
        )
    return model

def get_model_no_random_seed(model_type,max_tokens,min_tokens,decoding,temperature,repetition):
    generate_params = {
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.MIN_NEW_TOKENS: min_tokens,
        GenParams.DECODING_METHOD: decoding,
        GenParams.TEMPERATURE: temperature,
        GenParams.REPETITION_PENALTY: repetition,
    }
    model = Model(
        model_id=model_type,
        params=generate_params,
        credentials=credentials,
        project_id=project_id
        )
    return model

model_type = "ibm/granite-13b-instruct-v2"
max_tokens = 350
min_tokens = 150
decoding = DecodingMethods.SAMPLE
temperature = 0.2
repetition=1.2
random_seed=1234

def extract_main_text_from_html(file):
    soup = bs4.BeautifulSoup(file, 'html.parser')
    # Extracting all paragraph tags
    paragraphs = soup.find_all('p')
    main_text = ' '.join([para.get_text() for para in paragraphs])
    return main_text

def get_model_stop(model_type,max_tokens,min_tokens,decoding,temperature,repetition,random_seed,stop_sequences):
    generate_params = {
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.MIN_NEW_TOKENS: min_tokens,
        GenParams.DECODING_METHOD: decoding,
        GenParams.TEMPERATURE: temperature,
        GenParams.REPETITION_PENALTY: repetition,
        GenParams.RANDOM_SEED: random_seed,
        GenParams.STOP_SEQUENCES:stop_sequences
    }
    model = Model(
        model_id=model_type,
        params=generate_params,
        credentials=credentials,
        project_id=project_id
        )
    return model

response = discovery.query(
        project_id=wd_project_id,
        collection_ids=[wd_collection_id],
        filter="document_id::" + doc_ids[1],
        query=dql_query,
        return_=flds,
    ).get_result()


file_name=['1_Why Digital Tokenization Is a Priority for the ETF Industry _ State Street.pdf','2_AI and the Future of Intelligent Investing _ State Street.pdf',  '3_Accelerating Data-Driven Investing _ State Street.pdf', '4_Five Questions Investors Should Be Asking About Outsourced Trading _ State Street.pdf', '5_The Multi-Asset Era Demands a Public-Private Model_State Street.pdf']
doc_ids=['12eb527c5dbc8754b75f9379532329c3',
 '06245a2a34362182f8d17b80e0b769b2',
 '26e6045593d9a1b5ef1ac153e05815e3',
 'b4cb7e9d7766423994e6ab6f9df874a3',
 'a2b85dbbc00f2c605ce887c339a3c379']
bullet_1=[]
for i in range(5):
    # Splitting at underscores and taking the second part
    title_with_extra = file_name[i].split('_')[1]
    # Splitting at the last underscore and taking the first part
    title = title_with_extra.rsplit(' _', 1)[0]
    response = discovery.query(
        project_id=wd_project_id,
        collection_ids=[wd_collection_id],
        filter="document_id::" + doc_ids[i],
        query=dql_query,
        return_=flds,
    ).get_result()
    test=re.sub(r'[^A-Za-z0-9.,;:\'\"!?() -]', '', extract_main_text_from_html(response["results"][0]['html'][0]))
    liability_phrase = "Share "
    if liability_phrase in test:
        clean_text = test.split(liability_phrase)[0]
    else:
        clean_text=test
    liability_phrase2 = "Featuring  "
    if liability_phrase2 in clean_text:
        clean_text_re = clean_text.split(liability_phrase2)[0]
    else:
        clean_text_re=clean_text
    clean_text_re=re.sub(r'\s{3,}','',clean_text_re)
    
    model_type = "ibm/granite-13b-instruct-v2"#
    max_tokens = 250
    min_tokens = 50
    decoding = DecodingMethods.GREEDY
    temperature = 0.7
    repetition=1.2
    random_seed=1234
    model=get_model(model_type,max_tokens,min_tokens,decoding,temperature,repetition,random_seed)
    #head_line='AI and the Future of Intelligent Investing'
    instruction = f"""
    You are a content editor at a major financial institution who is responsible for thought leadership writing. 
    Read the given article about {title} carefully and explain the opportunity or challenge that this article provides for the reader in complete sentences.
    You should rely strictly on the provided text, without including any external information
    """

    input_prefix  = 'Article:'
    output_prefix = 'Opportunity or Challenge:'

    prompts = f"""{instruction} 
    {input_prefix} {clean_text_re}
    {output_prefix}
                """
    model_response=model.generate_text(prompt=prompts)
    print(title)
    print(model_response)
    print('----------------------------------')
    bullet_1.append(model_response)



file_name=['1_Why Digital Tokenization Is a Priority for the ETF Industry _ State Street.pdf','2_AI and the Future of Intelligent Investing _ State Street.pdf',  '3_Accelerating Data-Driven Investing _ State Street.pdf', '4_Five Questions Investors Should Be Asking About Outsourced Trading _ State Street.pdf', '5_The Multi-Asset Era Demands a Public-Private Model_State Street.pdf']
doc_ids=['12eb527c5dbc8754b75f9379532329c3',
 '06245a2a34362182f8d17b80e0b769b2',
 '26e6045593d9a1b5ef1ac153e05815e3',
 'b4cb7e9d7766423994e6ab6f9df874a3',
 'a2b85dbbc00f2c605ce887c339a3c379']
bullet_2=[]
for i in range(5):
    # Splitting at underscores and taking the second part
    title_with_extra = file_name[i].split('_')[1]
    # Splitting at the last underscore and taking the first part
    title = title_with_extra.rsplit(' _', 1)[0]
    response = discovery.query(
        project_id=wd_project_id,
        collection_ids=[wd_collection_id],
        filter="document_id::" + doc_ids[i],
        query=dql_query,
        return_=flds,
    ).get_result()
    test=re.sub(r'[^A-Za-z0-9.,;:\'\"!?() -]', '', extract_main_text_from_html(response["results"][0]['html'][0]))
    liability_phrase = "Share "
    if liability_phrase in test:
        clean_text = test.split(liability_phrase)[0]
    else:
        clean_text=test
    liability_phrase2 = "Featuring  "
    if liability_phrase2 in clean_text:
        clean_text_re = clean_text.split(liability_phrase2)[0]
    else:
        clean_text_re=clean_text
    clean_text_re=re.sub(r'\s{3,}','',clean_text_re)
    
    model_type = "ibm/granite-13b-instruct-v2"#
    max_tokens = 250
    min_tokens = 50
    decoding = DecodingMethods.GREEDY
    temperature = 0.7
    repetition=1.2
    random_seed=1234
    model=get_model(model_type,max_tokens,min_tokens,decoding,temperature,repetition,random_seed)
    #head_line='AI and the Future of Intelligent Investing'
    instruction = f"""
    You are a content editor at a major financial institution who is responsible for thought leadership writing. 
    Read the given article about {title} carefuly and explains what would be the consequences of ignoring the opportunity or challenge mentioned in the article in complete sentences.
    You should rely strictly on the provided text, without including any external information
    """

    input_prefix  = 'Article:'
    output_prefix = 'Opportunity or Challenge:'

    prompts = f"""{instruction} 
    {input_prefix} {clean_text_re}
    {output_prefix}
                """
    model_response=model.generate_text(prompt=prompts)
    print(title)
    print(model_response)
    print('----------------------------------')
    bullet_2.append(model_response)
    
    file_name=['1_Why Digital Tokenization Is a Priority for the ETF Industry _ State Street.pdf','2_AI and the Future of Intelligent Investing _ State Street.pdf',  '3_Accelerating Data-Driven Investing _ State Street.pdf', '4_Five Questions Investors Should Be Asking About Outsourced Trading _ State Street.pdf', '5_The Multi-Asset Era Demands a Public-Private Model_State Street.pdf']
doc_ids=['12eb527c5dbc8754b75f9379532329c3',
 '06245a2a34362182f8d17b80e0b769b2',
 '26e6045593d9a1b5ef1ac153e05815e3',
 'b4cb7e9d7766423994e6ab6f9df874a3',
 'a2b85dbbc00f2c605ce887c339a3c379']
bullet_2_re=[]
for i in range(5):
    # Splitting at underscores and taking the second part
    title_with_extra = file_name[i].split('_')[1]
    # Splitting at the last underscore and taking the first part
    title = title_with_extra.rsplit(' _', 1)[0]
    response = discovery.query(
        project_id=wd_project_id,
        collection_ids=[wd_collection_id],
        filter="document_id::" + doc_ids[i],
        query=dql_query,
        return_=flds,
    ).get_result()
    test=re.sub(r'[^A-Za-z0-9.,;:\'\"!?() -]', '', extract_main_text_from_html(response["results"][0]['html'][0]))
    liability_phrase = "Share "
    if liability_phrase in test:
        clean_text = test.split(liability_phrase)[0]
    else:
        clean_text=test
    liability_phrase2 = "Featuring  "
    if liability_phrase2 in clean_text:
        clean_text_re = clean_text.split(liability_phrase2)[0]
    else:
        clean_text_re=clean_text
    clean_text_re=re.sub(r'\s{3,}','',clean_text_re)
    
    model_type = "ibm/granite-13b-instruct-v2"#
    max_tokens = 200
    min_tokens = 50
    decoding = DecodingMethods.GREEDY
    temperature = 0.8
    repetition=1.2
    random_seed=1234
    model=get_model(model_type,max_tokens,min_tokens,decoding,temperature,repetition,random_seed)
    #head_line='AI and the Future of Intelligent Investing'
    instruction = f"""
    You're the content editor at a major financial institution, responsible for thought leadership
    Your task is to generate a clear and concise summary of the given article on {title}
    Focus on explaining the opportunities highlighted in the article that are particularly relevant
    """

    input_prefix  = 'Article:'
    output_prefix = 'Summary:'

    prompts = f"""{instruction} 
    {input_prefix} {clean_text_re}
    {output_prefix}
    """
    
    #print(prompts)
    model_response=model.generate_text(prompt=prompts)
    print(title)
    print(model_response)
    print('----------------------------------')
    bullet_2_re.append(model_response)
