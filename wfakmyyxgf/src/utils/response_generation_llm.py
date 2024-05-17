import pandas as pd
import time
import os
from dotenv import load_dotenv
from watson_CE_modules import watson_x

load_dotenv()
api_key_env = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)

def response_generation_llm(df):
    """
    Function for response generation using llm
    Arguments:
    df = pandas dataframe
    Example = df_name
    Returns:
    Pandas Dataframe
    """
    for index, row in df.iterrows():
        word_count = len(str(row['Review Text']).split())
        if word_count <= 2:
            #df.at[index, 'Review Text'] = "Thanks for your feedback. Happy to hear more!" if row['Star Rating'] < 3 else "Thankyou for sharing your feedback. We will continue to serve you"
            prompt=f"""<s>[INST] <<SYS>>Please generate response based on the review text and the rating {row['Review Text']} that is given. The generated response has to start with "Hi User, .." Please don't add any other additional information or don't add any further explanation. Keep the generated response within 2 lines and within 100 words and don't provide any other additional information. Consider the rating and give the responses. {row['Star Rating']} is the rating given. If {row['Star Rating']} is less than 3, then the response has to start with "Hi User, Sorry, to hear..". If {row['Star Rating']} is more than 3, then the response has to start with "Hi User, Thanks for the feedback. We're glad to hear that..". If {row['Star Rating']} is 3, then the response has to start with "Hi User,.." and it has to be based on the review text given. Only one response has to be generated and don't add any further explanation. Don't generate additional responses for different ratings. Only one response needs to be generated. Add "company-name.co.in" in the response for contact details. The response generated has to end with "Thanks! Team company-name"
                    <</SYS>>
                    Input: {row['Review Text']}
                    [/INST]
                    Output: """
            prompt=[prompt]
            wxObj = watson_x.WatsonXCE(api_key_env, ibm_cloud_url, wx_project_id)
            response=wxObj.wx_send_to_watsonxai(prompt,"meta-llama/llama-2-70b-chat", "sample", 4095, 1, 0, 1, [])
            print(response)
            df.loc[index, 'Generated_Response'] = response
        else:
            if row['Response'] is not None: #If there is standard response
                # print("Response_llm")
                response_df = row['Response']
                issue_df = row['predicted_issue']
                rating = row['Star Rating']
                prompt=f"""<s>[INST] <<SYS>>You are a helpful, respectful and honest assistant. Your job is to generate response for the review text that is given based on the standard response {response_df}, the predicted issue {issue_df} and the review text. If there are multiple issues then generate a single response and dont generate responses for all issues. The generated response has to be similar to the response given and while generating the response consider the issue that is given so that response is aligned to the issue given. Please add “Hi User, .. to the start of the response . Please don’t add any other additional information. If {rating} is more than 3, Generate response starting with "Hi User, Thanks for the feedback. We're glad to hear that.." and the response has to be positive only. If {row['Star Rating']} is 3, then the response has to start with "Hi User,..". If {rating} is less than 3, Generate response starting with "Hi User, Sorry to hear that..". Keep the generated response within 2 lines and within 100 words and don't add any additional information. The response has to be generated with issue, review text and standard responses. The response should also have the phrases in the given review text as well and please try to make the response more specific to the review text that is given. Only one response has to be generated and don't add any further explanation about issues, review text and the standard response. Don't generate additional responses for different ratings. Only one response needs to be generated. Add "company-name.co.in" in the response for contact details. The response generated has to end with "Thanks! Team company-name.".
                    <</SYS>>
                    Input: {row['Review Text']}
                    [/INST]
                    Output: """
                prompt=[prompt]
            else: #If there is no standard response
                prompt=f"""<s>[INST] <<SYS>>Please generate response for the review text given. The generated response has to start with "Hi User, .." Please don't add any other additional information. Keep the generated response within 2 lines and don't provide any other additional information. Only 1 response has to be generated and don't add any further explanation about issues, review text and standard response. Don't generate additional responses for different ratings. Only one response needs to be generated. Add "company-name.co.in" in the response for contact details.
                    <</SYS>>
                    <</SYS>>
                    Input: {row['Review Text']}
                    [/INST]
                    Output: """
                prompt=[prompt]
            time.sleep(1)
            wxObj = watson_x.WatsonXCE(api_key_env, ibm_cloud_url, wx_project_id)
            response=wxObj.wx_send_to_watsonxai(prompt,"meta-llama/llama-2-70b-chat", "sample", 4095, 1, 0, 1, [])
            print(response)
            df.loc[index, 'Generated_Response'] = response
    return df