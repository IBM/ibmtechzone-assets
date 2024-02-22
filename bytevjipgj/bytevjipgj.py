import os
import pandas as pd
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models import Model
from sklearn.metrics import f1_score
from multiprocessing import Pool

WATSONXAI_ENDPOINT = os.environ["watsonxai_endpoint"]
IBMCLOUD_APIKEY = os.environ["ibmcloud_apikey"]
PROJECT_ID = os.environ["project_id"]

credentials = {
    "url": WATSONXAI_ENDPOINT,
    "apikey": IBMCLOUD_APIKEY
}

parameters = {
    GenParams.MAX_NEW_TOKENS: 15
}

project_id = PROJECT_ID

object_key = 'test.csv'

model_id = ModelTypes.FLAN_UL2

model = Model(
    model_id=model_id,
    params=parameters,
    credentials=credentials,
    project_id=project_id)

def prompt_and_score(args):
    input_text, prompt_text, area = args
    result = model.generate_text(prompt=" ".join([prompt_text, input_text]))
    return f1_score([area], [result], average='micro')

def process_file(prompt_file):
    with open("data/" + prompt_file, 'r') as file:
        prompt_str = file.read()
        print("\nCurrently evaluating prompt: " + prompt_file + "\n")
        prompt_args = [(input_text, prompt_str, area) for input_text, area in zip(test_data.Customer_Service, test_data.Business_Area)]
        with Pool() as pool:
            scores = pool.map(prompt_and_score, prompt_args)
        avg_score = sum(scores) / len(scores)
        print('f1_micro_score', avg_score)
        print("\n=====================================\n")
        return avg_score

test_data = pd.read_csv("data/" + object_key)
test_data = test_data.head(10)

prompt_files = [f for f in os.listdir("data/") if f.endswith(".txt")]

output_data = {'Prompt_File': [], 'F1_Micro_Score': []}

for prompt_file in prompt_files:
    avg_score = process_file(prompt_file)
    output_data['Prompt_File'].append(prompt_file)
    output_data['F1_Micro_Score'].append(avg_score)

output_df = pd.DataFrame(output_data)
output_df.to_csv('results.csv', index=False)