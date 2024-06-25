import pickle 
import re
import os
import pandas as pd
from ibm_watsonx_ai.foundation_models import Model
from Template import Emory_Johns_Creek
from dotenv import load_dotenv
load_dotenv()




hospital_name_dict = {'Emory Johns Creek':Emory_Johns_Creek}



project_id = os.getenv("watson_ai_project_id")

model_id = "mistralai/mixtral-8x7b-instruct-v01"
watson_ai_api_key = os.getenv('watson_ai_api_key')


parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 512,
    "min_new_tokens": 10,
    "repetition_penalty": 1,
    "random_seed":42
}

def get_credentials():
	return {
		"url" : "https://us-south.ml.cloud.ibm.com",
		"apikey" : watson_ai_api_key 
	}




model = Model(
	model_id = model_id,
	params = parameters,
	credentials = get_credentials(),
	project_id = project_id,
	)


if __name__== "__main__":

    subset_df =  pd.read_excel('subset_df.xlsx')

    visit_dict = {}
    visit_count = 0
    for ind,row in subset_df.iterrows():
        data = row[1]
        for hospital_name in hospital_name_dict.keys():
            if len(re.findall(hospital_name,data[0],re.IGNORECASE))>0:
                # print(key)
                for prompt in hospital_name_dict[hospital_name]:
                    resp = ''
        
                    resp = model.generate_text(prompt.format(data),guardrails=False)
                    ind = re.search('Visit Present:',resp,re.IGNORECASE)
                    # print(ind,'ind')
                    if ind :
                        if re.search('yes',resp,re.IGNORECASE):
                            number_of_visits = re.search(r"Number of visits:\s*(\d+)",resp,re.IGNORECASE).group(1)
                            if not number_of_visits:
                                number_of_visits =1
                            visit_count += 1
                            visit_dict[visit_count] = {'page_number':row[0],'visit_count':number_of_visits}

    pickle.dump(visit_dict,open('visit_dict.pkl','wb'))

                
                
                
