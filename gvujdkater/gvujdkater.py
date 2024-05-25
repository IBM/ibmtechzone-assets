# Import required libraries
import os 
import numpy as np


# Set env variables
BAM_API_KEY = os.environ["bam_api_key"]
WATSONX_API_KEY = os.environ["watsonx_api_key"]
IBM_CLOUD_URL = os.environ["ibm_cloud_url"]
PROJECT_ID = os.environ["project_id"]


# Boolean to decide whether to use BAM or WatsonX.ai GA
USER_BAM = True


# Sample news article data
news_articles = [
    {
        "title": "Challenges in Distributing COVID-19 Vaccines to Rural Areas",
        "content": "In the race to vaccinate against COVID-19, rural areas face significant challenges. According to recent statistics, only 30% of rural populations have received their first vaccine dose. Dr. Sarah Johnson, a leading epidemiologist, highlights the disparities in vaccine distribution. Remote regions like Pine County, with a population of 50,000, struggle with vaccine accessibility. Transportation infrastructure limitations exacerbate the situation, leading to logistical hurdles. Health officials are exploring innovative solutions, such as mobile vaccination clinics. The rollout plan aims to prioritize high-risk demographics and essential workers. Funding shortages pose a major obstacle to the deployment of vaccination programs. Despite challenges, community outreach efforts have shown promising results in some areas. Collaboration between healthcare providers and local governments is key to overcoming barriers."
    },
    {
        "title": "Quantum Computing Breakthrough: Advancements in Superconducting Qubits",
        "content": "Scientists at QuantumTech Labs announce a groundbreaking achievement in quantum computing. The research team, led by Dr. Emily Chang, has made significant strides in superconducting qubit technology. QuantumTech's latest quantum processor prototype boasts a record-breaking qubit count of 1024. The increased qubit density marks a crucial milestone in the quest for scalable quantum computing. Dr. Chang explains that the breakthrough opens doors to solving complex computational problems. Superconducting qubits, with their low error rates, offer promising prospects for practical quantum applications. The development paves the way for quantum supremacy, surpassing classical computing capabilities. Industry experts anticipate transformative impacts across various fields, from cryptography to drug discovery. QuantumTech plans to collaborate with leading research institutions to further refine the technology. Despite challenges, the quantum computing community remains optimistic about the future."
    }
]


# Setup the prompt for news article summarization
SUMMARY_PROMPT = """
[INST] <<SYS>>
Summarize the key points of the given news article in 1-2 lines. 
<</SYS>>
News:
{news_para}
[/INST]
"""


# Calculating log probabilities for confidence assessment of LLM response (https://gautam75.medium.com/unlocking-llm-confidence-through-logprobs-54b26ed1b48a)
# Method 1: Average of Log Probabilities
def calculate_confidence_log_probs(log_probs):
    avg_log_prob = np.mean(log_probs)
    return -avg_log_prob  # closer to 0 indicates higher confidence


# Method 2: Converting to Linear Probabilities
def calculate_confidence_linear_probs(log_probs):
    linear_probs = np.round(np.exp(log_probs)*100,2)
    confidence = np.mean(linear_probs)
    return confidence  # closer to 100 indicates higher confidence


# Get response
if USER_BAM:
    from genai import Credentials, Client
    from genai.schema import TextGenerationParameters, TextGenerationReturnOptions

    creds = Credentials(api_key = BAM_API_KEY, api_endpoint = "https://bam-api.res.ibm.com")
    client = Client(credentials = creds)

    for article in news_articles:
        response = list(client.text.generation.create(
        model_id="mistralai/mixtral-8x7b-instruct-v01", 
        inputs=SUMMARY_PROMPT.format(news_para = article['content']), 
        parameters=TextGenerationParameters(
            max_new_tokens=200, 
            min_new_tokens=20, 
            decoding_method="greedy", 
            stop_sequences=["</s>"], 
            return_options=TextGenerationReturnOptions(
                generated_tokens=True,
                input_text=True,
                input_tokens=True,
                input_parameters=True,
                token_logprobs=True,
                token_ranks=True,
                top_n_tokens=2))))
        
        result = response[0].results[0]
        generated_tokens = response[0].results[0].generated_tokens
        log_probs = [token.top_tokens[0].logprob for token in generated_tokens]
        confidence_linear_probs = calculate_confidence_linear_probs(log_probs)
        
        print("NEWS TITLE:", article['title'])
        print("GENERATED SUMMARY:", result.generated_text.strip(), "\n")
        print("INPUT TEXT TOKEN COUNT:", result.input_token_count)
        print("GENERATED TEXT TOKEN COUNT:", result.generated_token_count)
        print(f"CONFIDENCE USING LINEAR PROBABILITIES:  {round(confidence_linear_probs, 2)}%\n")
        print("--"*50)
   
else:
    from ibm_watson_machine_learning import APIClient
    from ibm_watson_machine_learning.foundation_models import Model 
    from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
    from ibm_watson_machine_learning.metanames import GenTextReturnOptMetaNames

    generate_params = {
        GenParams.MAX_NEW_TOKENS: 200,
        GenParams.MIN_NEW_TOKENS: 20,
        GenParams.DECODING_METHOD: "greedy",
        GenParams.STOP_SEQUENCES: ["</s>"],
        GenParams.RETURN_OPTIONS: {
            GenTextReturnOptMetaNames.INPUT_TEXT: False,
            GenTextReturnOptMetaNames.INPUT_TOKENS: True,
            GenTextReturnOptMetaNames.GENERATED_TOKENS: True,
            GenTextReturnOptMetaNames.TOKEN_LOGPROBS: True,
            GenTextReturnOptMetaNames.TOKEN_RANKS: True,
            GenTextReturnOptMetaNames.TOP_N_TOKENS: 2
        }
    }

    model = Model(
        model_id = "mistralai/mixtral-8x7b-instruct-v01",
        params = generate_params,
        project_id = PROJECT_ID,
        credentials={
            "apikey": WATSONX_API_KEY,
            "url": IBM_CLOUD_URL
        }
    )

    for article in news_articles:
        prompt = SUMMARY_PROMPT.format(news_para = article['content'])
        
        response = model.generate(prompt=[prompt])
        result = response[0]['results'][0]

        generated_tokens = result['generated_tokens']
        log_probs = [token['top_tokens'][0]['logprob'] for token in generated_tokens if len(token['top_tokens']) > 1 and "logprob" in token['top_tokens'][0]]
        confidence_linear_probs = calculate_confidence_linear_probs(log_probs)

        print("NEWS TITLE:", article['title'])
        print("GENERATED SUMMARY:", result['generated_text'].strip(), "\n")
        print("INPUT TEXT TOKEN COUNT:", result["input_token_count"])
        print("GENERATED TEXT TOKEN COUNT:", result["generated_token_count"])
        print(f"CONFIDENCE USING LINEAR PROBABILITIES:  {round(confidence_linear_probs, 2)}%\n")
        print("--"*50)