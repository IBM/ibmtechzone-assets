import time
import os
import regex as re
from dotenv import load_dotenv
from watson_CE_modules import watson_x

load_dotenv()
api_key_env = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)


# Function to identify predictions which don't match with the ground truths
def extracted_issue_prediction(test_data):
    
    i = 0 # No for iteration in dataframe.
    max_column = len(test_data.columns)-1
    for review_text in test_data["Review Text"]:
        prompt = f"""<s> <<SYS>> [INST] Your job is to extract the bad key words from the review text that seems negative. If the review text seems positive, then output empty list. If the review text seems neither positive nor negative and meaningless, then output empty list. Don't provide additional information apart from the keywords extracted from the review text. Please, don't give any explanation. Consider below examples while extracting the bad keywords and answer accordingly.
        Example 1: 
        Input : In this app when transaction is successful this app is showing failed message Transection history also not seen in this application This is worst application
        Output : [Failed message, not seen, worst application]
        Example 2:
        Input :  Very bad experience there is no any option to show account number and transfer historylook like fraud aap
        Output : [bad experience, no any option, fraud app]
        Example 3:
        Input : It is taking too much time to open the app Many of the time the initialising time is around 1 minute
        Output : [taking too much time]
        Example 4:
        Input :  shows you havent updated even after installing it just now
        Output : [not updated]
        Example 5: 
        Input : my phone boi please
        Output : []
        Example 6: 
        Input : Bs ohi 
        Output : []
        <</SYS>> 
        Input : {review_text}
        [/INST] 
        Output :"""
    
        prompt = [prompt]

        time.sleep(1)

        # Object creation
        wxObj = watson_x.WatsonXCE(api_key_env, ibm_cloud_url, wx_project_id)
    
        # Response generation
        predicted_keywords = wxObj.wx_send_to_watsonxai(prompts=[prompt],
			model_name="meta-llama/llama-2-70b-chat", \
			decoding_method="greedy",\
			max_new_tokens=30,\
			min_new_tokens=1, \
			temperature=0, \
            repetition_penalty=1.0, \
            stop_sequences=["\n\n", "Note:"])

        # To save the predicted issue in predicted_issue column
        filter_kwd = str(predicted_keywords[0]).split('\n\n')
        keywords = str(filter_kwd[0]).strip()
        keywords = keywords.replace('[','')
        keywords = keywords.replace(']','')
        print(i, "keywords", keywords)
        test_data.iloc[i, max_column-1] = keywords
        
        if test_data.iloc[i,max_column-3] == 'Good':
            test_data.iloc[i,max_column] = 0
        else:
            if keywords.find(', ')!=-1:
                test_data.iloc[i,max_column] = keywords.count(',') + 1
            elif len(keywords)>1:
                test_data.iloc[i,max_column] = 1
            else:
                test_data.iloc[i,max_column] = 0
        i+=1
    return test_data
