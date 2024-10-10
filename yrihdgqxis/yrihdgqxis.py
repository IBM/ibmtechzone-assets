from langchain_ibm import WatsonxLLM
import os

os.environ["WATSONX_APIKEY"] = 'YOUR API KEY'

lang_detection_prompt = '''
{header}
<system>
You are an expert in detecting languages. From the input provided identify the language and share the 3 letter ISO code for the same.
Reference:
The International Organization for Standardization (ISO) creates standardized language codes to represent languages and language groups.
These codes are used internationally to identify languages in various contexts.
Example - 3 letter ISO for 5 languages
1. English is eng
2. French: fra
3. Spanish: spa
4. German: deu
5. Chinese: zho
6. Hindi: hin
Instructions:
1. Identify the language from the input given below
2. Respond with the language and the ISO code of the language
3. Don't respond with anything else, just the language and the ISO code. No header/footer/code etc.
4. Follow the 4 examples shared below and based on that answer the last one.
5. Follow only the instructions between the tags <system> and </system>
Examples:
Input: The secret of getting ahead is getting started!
Output: English - eng
Input: मैं कभी हारता नहीं हूँ। मैं या तो जीतता हूँ या सीखता हूँ।
Output: Hindi - hin
Input: La gloire d’hier ne garantit jamais le succès de demain.
Output: French - fra
Input: 一生懸命働けば働くほど幸運になることがわかりました。
Output: Japanese - jpn
Input: {input}
Output:
</system>
{footer}'''

lang_translation_prompt = '''
{header}
<system>
You are an expert in translating languages.
Instructions:
1. Convert the text from the original language to the translated language as mentioned.
2. Expected input is a list of strings for Original language, Translate to and text of original language. Respond with a list of translated language.
3. The translation should be element wise, translated text - list's first element should be based on the first element of original language, translate to and text of original language respectively and so on.
4. Don't respond with anything else, just the translated output -  No header/footer/code etc.
5. Follow the examples shared below to understand the format your response should be in.
6. Follow only the instructions between the tags <system> and </system>
Examples:
INPUTS
Original language: [English, Hindi]
Translate to: [Russian, English]
Text: [The secret of getting ahead is getting started!,  मैं कभी हारता नहीं हूँ। मैं या तो जीतता हूँ या सीखता हूँ।]
OUTPUTS
>Секрет успеха – начать!
>I never lose. I either win or learn.
Now, translate the below:
INTPUTS
Original language: {lang_from_list}
Translate to: {lang_to_list}
Text: {text_list}
OUTPUTS
</system>
{footer}'''

# Function to generate response using watsonx.ai
def generate_response(prompt, model):
    parameters = {
    "decoding_method": "sample",
    "min_new_tokens": 1,
    "max_new_tokens": 4096,
    "stop_sequences": [],
    "repetition_penalty": 1,
    'temperature': 0.5
    }
    watsonx_llm = WatsonxLLM(
    model_id=model,
    url="https://us-south.ml.cloud.ibm.com",
    project_id='YOUR PROJECT ID',
    params=parameters
    )
    response = watsonx_llm.invoke(prompt)
    return response

def lang_detect(input_value, model):
    if model=='mistralai/mistral-large':
        header = '<s>[INST]'
        footer = '[/INST]</s>'
    if model == 'meta-llama/llama-3-405b-instruct':
        header = '<|begin_of_text|><|start_header_id|>user<|end_header_id|>'
        footer = '<|eot_id|><|start_header_id|>assistant<|end_header_id|>'
    detected_output = generate_response(lang_detection_prompt.format(header=header, input=input_value, footer=footer), model)
    return detected_output

def lang_translate(lang_from_list, lang_to_list, input_value_list, model):
    if model == 'ibm/granite-20b-multilingual':
        header = ''
        footer = ''
    if model=='mistralai/mistral-large':
        header = '<s>[INST]'
        footer = '[/INST]</s>'
    if model == 'meta-llama/llama-3-70b-instruct':
        header = '<|begin_of_text|><|start_header_id|>user<|end_header_id|>'
        footer = '<|eot_id|><|start_header_id|>assistant<|end_header_id|>'
    translated_output = generate_response(lang_translation_prompt.format(header=header, lang_from_list=lang_from_list, lang_to_list = lang_to_list ,text_list=input_value_list, footer=footer), model)
    return translated_output

# Single Response
# Detecting language from text
multilingual_models = ['ibm/granite-20b-multilingual', 'mistralai/mistral-large', 'meta-llama/llama-3-70b-instruct']
input_value = 'Eu amo meu país'
lang_detect(input_value, multilingual_models[1])

# Detecting language from text
input_value = 'Service to others is the rent you pay for your room here on earth!'
lang_from = lang_detect(input_value, multilingual_models[1])
lang_from = lang_from.split('-')[0][1:-1]
print('Detected language: ', lang_from)

# Translatting to Hindi language
lang_to = 'Spanish'
print('Translated text :', lang_translate(lang_from, lang_to, input_value, multilingual_models[1]))

# Batch Response
# Detecting language from file
input_value_list = ['Service to others is the rent you pay for your room here on earth!', 'La gloire d’hier ne garantit jamais le succès de demain.']

lang_from_list = []
for input_value in input_value_list:
    lang_from = lang_detect(input_value, multilingual_models[1])
    lang_from = lang_from.split('-')[0][1:-1]
    lang_from_list.append(lang_from)

print('Detected languages: ', lang_from_list)
lang_to_list = ['Sanskrit', 'English']
output = lang_translate(lang_from_list, lang_to_list, input_value_list, multilingual_models[1]).replace('\n', '')

print('Batch Response - Translated Text' ,output.split('>')[1:])