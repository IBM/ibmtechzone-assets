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

q = "Premise:  At my age you will probably have learnt one lesson. Hypothesis:  It's not certain how many lessons you'll learn by your thirties. Does the premise entail the hypothesis?"
generated_response = model.generate(prompt=q)
print(generated_response['results'][0]['generated_text'])
