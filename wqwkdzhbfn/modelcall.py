import getpass
import os
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models import ModelInference

credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "vFOCKSvI3OHpk_GRTQfnuFHHKbdqWgfrRn5Sh6a5X7Jv"
}



try:
    project_id = os.environ["PROJECT_ID"]
except KeyError:
    project_id = '998db0c2-ee10-41bf-bc2a-e0b34477edae'



model_id = "ibm-mistralai/mixtral-8x7b-instruct-v01-q"



parameters = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 800,
    GenParams.STOP_SEQUENCES: ["<end·of·code>"]
}


model = ModelInference(
    model_id=model_id, 
    params=parameters, 
    credentials=credentials,
    project_id=project_id)




def get_result(text):
    text = '<instructions> \n' + text + ' \n </instructions>'
    # print("TEXT:::", text)
    response = model.generate_text(text)
    return response
