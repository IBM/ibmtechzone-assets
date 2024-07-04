import time
import os
import regex as re
from dotenv import load_dotenv
import watson_x

load_dotenv()
api_key_env = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)

# Function to do the prediction and identify predictions which don't match with the ground truths
def false_prediction(test_data):
    
    i = 0 # No for iteration in dataframe.
    # i = test_data.index[0] # only to be used when you are starting from 0th index otherwise it will cause error while putting the prediction in your test dataframe
    # as it may not find the desired row to fill in.
    TP = 0 # No of matched strings/results.
    false_prediction_index = []
    for review_text in test_data["review_text"]:
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

        str1 = test_data.loc[i,'predicted_issue']
        str2 = test_data.loc[i,'issue_ground_truth']

        # Replacing unnecessary spaces.
        str1 = str1.replace(' ','')
        str2 = str2.replace(' ','')

        # Converting into lowerstream for betterr matching.
        str1 = str1.lower()
        str2 = str2.lower()
        if (str1.find(str2))!=-1 or (str2 in str1):
            TP += 1
        else:
            false_prediction_index.append(i) 
        i += 1

    # To save the dataset into excel containing ground truth and prediction made
    test_data.to_excel('GroundTruth_vs_Predictions.xlsx', index = False)
    return false_prediction_index