import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods

# To display example params enter
print(GenParams().get_example_values())

generate_params = {
    GenParams.MAX_NEW_TOKENS: 25
}
API_KEY = os.environ["apikey"]
URL = os.environ["url"]
PROJECT_ID = os.environ["project_id"]

model = Model(
    model_id=ModelTypes.FLAN_UL2,
    params=generate_params,
    credentials={
        "apikey": API_KEY,
        "url": URL
    },
    project_id=PROJECT_ID
    )

q = "The square root of x is the cube root of y. What is y to the power of 2, if x = 4?"
generated_response = model.generate(prompt=q)
print(generated_response['results'][0]['generated_text'])
os.environ['mysquareroot'] = int(generated_response['results'][0]['generated_text'].split("=")[1])
