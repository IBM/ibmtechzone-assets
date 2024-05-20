import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

def get_wml_creds():
    load_dotenv()
    api_key = os.getenv("API_KEY", None)
    ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
    project_id = os.getenv("PROJECT_ID", None)
    if api_key is None or ibm_cloud_url is None or project_id is None:
        print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
    else:
        creds = {
            "url": ibm_cloud_url,
            "apikey": api_key 
        }
    return project_id, creds


project_id, creds = get_wml_creds()
greedy_params={
    "decoding_method": "greedy",
    # "stop_sequences": [
    #   "\n\n"
    # ],
    "min_new_tokens": 1,
    "max_new_tokens": 800,
    # "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }
def send_to_watsonxai(prompts,
                    model_name='meta-llama/llama-2-70b-chat',
                    decoding_method='sample',
                    max_new_tokens=400,
                    min_new_tokens=10,
                    temperature=0.1,
                    repetition_penalty=1.1,
                    stop_sequences=["Input:","Question:"]
                    ):
    '''
    helper function for sending prompts and params to Watsonx.ai
    
    Args:  
        prompts:list list of text prompts
        decoding:str Watsonx.ai parameter "sample" or "greedy"
        max_new_tok:int Watsonx.ai parameter for max new tokens/response returned
        temp:float Watsonx.ai parameter for temperature (range 0>2)

    Returns: None
        prints response
    '''
    #print("========== My Model =========")
    # GA version
    model_params = {
        GenParams.DECODING_METHOD: decoding_method,
        GenParams.MIN_NEW_TOKENS: min_new_tokens,
        GenParams.MAX_NEW_TOKENS: max_new_tokens,
        GenParams.RANDOM_SEED: 42,
        GenParams.TEMPERATURE: temperature,
        GenParams.REPETITION_PENALTY: repetition_penalty,
        GenParams.STOP_SEQUENCES: stop_sequences
    }

    # GA
    model = Model(
            model_id=model_name,
            params=greedy_params,
            credentials=creds,
            project_id=project_id)

    # GA
    for prompt in prompts:
        return model.generate_text(prompt)


# 5. Your responses should not be long and just have about 2-3 sentences.
RAG_PROMPT = """
Please answer the given question using input document. 

Intruction:
1. You will be given a document that must be used to reply to user questions.
2. You should generate response only using the information available in the input documents.
3. If you can't find an answer, strictly say only "I don't know".
4. If answer is not from Input Document, strictly say only "I don't know".
5. You should not repeat your answers.
6. Do not use any other knowledge.
7. Please generate the answer in tabular format while comparing kinds of questions.
8. Summarise the response in a precise manner and also don’t ask the questions.
9. Close the conversation with no further questions like system generated User questions.
10. Personal loan is different from education loan.

Input: 
{context_document}

Question: {query}

Output:
"""

#"\n\n".join(_docs['paragraph'])[:1000]

def get_watson_ai_output(query,document):
    try:
        response_1 = send_to_watsonxai(
                            prompts=[RAG_PROMPT.format(context_document=document, query=query)],
                            #model_name='google/flan-t5-xxl',
                            model_name='meta-llama/llama-2-70b-chat',
                            decoding_method='sample',
                            max_new_tokens=400,
                            min_new_tokens=10,
                            temperature=0.1,
                            repetition_penalty=1.1,
                            stop_sequences=["Input:","Question:"]
                        )
    except:
        response_1 = send_to_watsonxai(
                            prompts=[RAG_PROMPT.format(context_document=document[:3000], query=query)],
                            #model_name='google/flan-t5-xxl',
                            model_name='meta-llama/llama-2-70b-chat',
                            decoding_method='sample',
                            max_new_tokens=400,
                            min_new_tokens=10,
                            temperature=0.1,
                            repetition_penalty=1.1,
                            stop_sequences=["Input:","Question:"]
                        )
    return response_1

#pprint(icici_qa("How much amount I can put in Reccuring Deposit (RD)?"))