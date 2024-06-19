import pandas as pd
import pickle
import os
import re
from dotenv import load_dotenv
import ast
import concurrent.futures
from concurrent.futures import  as_completed

from ibm_watsonx_ai.foundation_models import Model

load_dotenv()




project_id = os.getenv("watson_ai_project_id")

model_id = "mistralai/mixtral-8x7b-instruct-v01"
watson_ai_api_key = os.getenv('watson_ai_api_key')





base_prompt1 = """Please extract the information under the following headings from the provided text. If a particular heading is not present, simply omit it from the results. Summarize information under heading section concisely, focusing on the key points.

Headings:"""

base_prompt2 = """
Please provide the summarized content for each available heading.

Please do not hallucinate.

Input: {}
Output:"""

common_attributes_list = []
dynamic_prompt_list = []


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


def make_one_prompt(generated_response_dict,base_prompt1,base_prompt2,common_attribute,context):
    
    
    common_attributes = '1' + '. ' + common_attribute
    
    # all_str = '\n'.join(common_attributes)

    final_prompt = base_prompt1 +'\n'+ common_attributes +base_prompt2.format(context)
    generated_response = model.generate_text(prompt=final_prompt, guardrails=False)
    generated_response_dict[common_attribute] = generated_response
    # print( generated_response_dict)
        

def make_prompt(common_attributes,context):
        generated_response_dict = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
                future = [executor.submit(make_one_prompt,generated_response_dict,base_prompt1,base_prompt2,attribute,context) for attribute in common_attributes]
                data =  [future.result() for future in as_completed(future)]
                # print(data)

        return generated_response_dict


if __name__== "__main__":
       



    complete_output_visit_start_end_type = pd.read_excel('complete_output_visit_start_end_type_content.xlsx')

    attribute_list = ['History of Illness',
    'History of Present Illness',
    'Problem List',
    'Physical Exam',
    'Medical Decision Making',
    'Reevaluation',
    'Assessment',
    'Plan',
    'Impression',
    'Findings',
    'Medication',
    'Report',
    'Discussion/Plan',
    'Complaint',
    'Indication'
    ]

    common_attributes_list = []
    dynamic_prompt_list = []

    for ind,row in  complete_output_visit_start_end_type.iterrows():
        print("ind--",ind)
        try:
            context = ast.literal_eval(row['p_context_list'])
            context = '/n'.join(context)
        except Exception as e:
            context = row['p_context_list']
            print('exception -------------------')

        common_attributes = []
        for attribute in attribute_list:

            matches = re.finditer(attribute,context,re.IGNORECASE)
            results = [match.group() for match in matches]
            if len(results)>0:
                common_attributes.append(results[0])
       
        common_attributes_list.append(common_attributes)
        dynamic_prompt_list.append(make_prompt(common_attributes,context))
        
        print("---------------------------------------------------------------------------------------------------------------------------")
        pickle.dump(dynamic_prompt_list,open('dynamic_prompt_list.pkl','wb'))
    

    
       
       