from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods
import os

# To display example params enter
#print(GenParams().get_example_values())
API_KEY = os.getenv('apikey')
WATSONXAI_URL = os.getenv('watsonxai_url')
PROJECT_ID = os.getenv('project_id')
MODEL_NAME = os.getenv('model_name')
PROMPT_QUESTION = os.getenv('prompt_question')

if PROMPT_QUESTION is None:
  PROMPT_FILE_NAME = os.getenv('prompt_file')
  print(PROMPT_FILE_NAME)
  PROMPT_FILE = open(PROMPT_FILE_NAME,"r")
  PROMPT_QUESTION = PROMPT_FILE.read()
  print(PROMPT_QUESTION)
  PROMPT_FILE.close()

generate_params = {
    GenParams.MAX_NEW_TOKENS: 25
}

model = Model(
    model_id=MODEL_NAME,
    params=generate_params,
    credentials={
        "apikey": API_KEY,
        "url": WATSONXAI_URL
    },
    project_id=PROJECT_ID
    )

generated_response = model.generate(prompt=PROMPT_QUESTION)
print(generated_response['results'][0]['generated_text'])
