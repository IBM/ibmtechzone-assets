# Text Streaming using Watsonx.AI
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import (
    ModelTypes,
    DecodingMethods,
)
import os
from dotenv import load_dotenv

load_dotenv()
generate_params = {GenParams.MAX_NEW_TOKENS: 2048}
model = Model(
    model_id="meta-llama/llama-3-70b-instruct",
    params=generate_params,
    credentials={"apikey": os.getenv("GA_API"), "url": os.getenv("GA_URL")},
    project_id=os.getenv("PROJECT_ID"),
)
q = "Write me a 100 words blog on LSTM."
generated_response = model.generate_text_stream(prompt=q)
print("type(generated_response): ", type(generated_response))
for i, chunk in enumerate(generated_response):
    print(chunk, end="")
    if i%20 == 0:
        print(end="\n")