import os
import getpass

def get_credentials():
	return {
		"url" : "https://us-south.ml.cloud.ibm.com",
		"apikey" : getpass.getpass("Please enter your api key (hit enter): ")
	}
model_id = "google/flan-ul2"
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "repetition_penalty": 1
}
project_id = os.getenv("PROJECT_ID")
space_id = os.getenv("SPACE_ID")
from ibm_watsonx_ai.foundation_models import Model

model = Model(
	model_id = model_id,
	params = parameters,
	credentials = get_credentials(),
	project_id = project_id,
	space_id = space_id
	)
input =  """On November 1st, 2023, at 11:00 am, my vehicle, a 2004 Honda Civic, was stolen from its parking spot in Lagos. I immediately reported the incident to the police and obtained a police report. The thief crashed my vehicle into a tree a few blocks away from the parking spot, causing significant damage to the front end. I have filed a claim for the damages and I am providing the police report as evidence of the theft and accident. The witnesses have also provided statements describing the incident.""" 

prompt_input = f"""You are an insurance agent tasked to assess insurance claims. Summarize the following insurance claim input. Focus on the car and the damage. Make the summary at least 3 sentences long.

Input: {input}
Output:"""


print("Submitting generation request...")
generated_response = model.generate_text(prompt=prompt_input, guardrails=True)
print(generated_response)