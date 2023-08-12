import os
import pandas as pd
from pandas import read_csv
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models import Model
from sklearn.metrics import f1_score

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

def prompt_and_score(test_data, prompt_text):
    results = []
    comments = list(test_data.Customer_Service)
    area = list(test_data.Business_Area)
    for input_text in comments:
        results.append(model.generate_text(prompt=" ".join([prompt_text, input_text])))
    print('f1_micro_score', f1_score(area, results, average='micro'))
    print("\n=====================================\n")

test_data = pd.read_csv("data/"+object_key)
test_data=test_data.head(3)

prompt_files = os.listdir("data/")
for i in range(0,len(prompt_files)):
    if prompt_files[i].endswith(".txt"):
        with open("data/"+prompt_files[i],'r') as file:
            promptStr = file.read()
            print("\nCurrently evaluating prompt: "+prompt_files[i]+"\n")
            prompt_and_score(test_data,promptStr)


