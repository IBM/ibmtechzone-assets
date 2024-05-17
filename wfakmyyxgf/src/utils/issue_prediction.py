import time
import os
import regex as re
from dotenv import load_dotenv
from watson_CE_modules import watson_x
load_dotenv()
api_key_env = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)


def split_common_issues(inputString):
    outList = inputString.split(', ')
    return outList

# Function to identify predictions which don't match with the ground truths
def issue_prediction(test_data):
    total_issue_list = []
    i = 0 # No for iteration in dataframe.
    max_column = len(test_data.columns)-1
    for review_text in test_data["Review Text"]:
        prompt = f"""<s><<SYS>>[INST]You are a helpul and trustworthy assistant. You job is to classify the review text as Account Details, Account Opening, ASBA IPO, Beneficiary, Bill Payments, Biometric Issue, Complex User Interface, Crash/Technical Error, Debit Card Issue, Device Issue, Download Issue, Font size, Fund Transfer, Installation, Keyboard Issue, Location Issue, Login/Registration Issue, MPIN issue, Onboarding Issue, OTP issue, Server Error, Sim Verification, Slow, Statements/Certificates, Transaction issue, UPI issue, Wifi issue by understanding the issue details from review text. Classify the negative review text as Generic if there's no details about the issue\n. Classify positive review text as Good\n. Only classify it\n. Don't explain it further only provide output in one or two words\n. If the isssue is related to keyboard, then classify it in Keyboard Issue. consider below example to predict the issue.
        Input: Mohd jabir m khan
        Output: Generic
        <</SYS>>
        Input: {review_text}
        [/INST]
        Output:"""
        
        prompt=[prompt]
        time.sleep(1)
        # Object creation
        wxObj = watson_x.WatsonXCE(api_key_env, ibm_cloud_url, wx_project_id)
        # Response generation
        predicted_isssue = wxObj.wx_send_to_watsonxai(prompts=[prompt],
            model_name="meta-llama/llama-2-70b-chat", \
            decoding_method="greedy",\
            max_new_tokens=20,\
            min_new_tokens=1, \
            temperature=0, \
            repetition_penalty=1.0, \
            stop_sequences=["\n", "Input:", "\n\n", "   ", "\t"])
        
        # To save the predicted issue in predicted_issue column
        # to create the list of all the issues for severity analysis
        filter_pred = str(predicted_isssue[0]).split('\n\n')
        issue = str(filter_pred[0]).strip()
        print(i, "predicted_issue:",issue)
        test_data.loc[i,'predicted_issue'] = issue   
        if(', ' in issue):
                splitIssue = split_common_issues(issue)
                if len(splitIssue) > 0:
                    for elem in splitIssue:
                        total_issue_list.append(elem)
        else:   
                total_issue_list.append(issue)
        i+=1
    print(total_issue_list)
    return test_data, total_issue_list