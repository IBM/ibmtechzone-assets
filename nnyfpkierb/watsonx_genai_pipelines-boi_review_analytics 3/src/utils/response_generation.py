import pandas as pd
import time
import os
from dotenv import load_dotenv
from watson_CE_modules import watson_x

load_dotenv()
api_key_env = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)

def response(df, file_name):

    """
    Function for adding the responses for the issues
    Arguments:
    df = pandas dataframe
    Example = df_name
    Returns:
    Pandas Dataframe
    """

    # Loading the file with issues and responses
    issues_responses_df = pd.read_excel(file_name)

    # Creating dictionary 
    issues_responses_dict = dict(zip(issues_responses_df['Issues'], issues_responses_df['Responses']))

    # Define a function to clean the response and add "Hi user"
    def clean_response(response):

        """
        Function for removing names
        Arguments:
        response = string
        Example = string_name
        Returns:
        string
        """

        if "hi" in response.lower():

            response_parts = response.split(",")
            response_after_comma = ",".join(response_parts[1:])  
            response_after_hi = response_after_comma.split("hi", 1)[-1]  
            response = "Hi user, " + response_after_hi.strip()  # Adding "Hi user" to the beginning
            return response

    def map_response(issue):

        """
        Function for mapping responses to issues
        Arguments:
        response = string
        Example = string_name
        Returns:
        string
        """

        if pd.isna(issue):
            return "Please help us understand this issue you are facing in depth by writing it to BOIMobileSupport@bankofindia.co.in. We will look into this with priority. Thank you, BOI team"
        elif issue not in issues_responses_dict:
            return "Please help us understand this issue you are facing in depth by writing it to BOIMobileSupport@bankofindia.co.in. We will look into this with priority. Thank you, BOI team"
        else:
            response = issues_responses_dict[issue]
            return clean_response(response)


    # Applying the function to the 'Issue' column 
    df.loc[:, 'Response'] = df['predicted_issue'].apply(map_response)

    for index, row in df.iterrows():

        if row['Response'] == 'Please help us understand this issue you are facing in depth by writing it to BOIMobileSupport@bankofindia.co.in. We will look into this with priority. Thank you, BOI team':
            
            if row['Star Rating'] >= 3:
                df.at[index, 'Response'] = 'Thanks for the feedback, Happy banking with BOI'
             
            elif row['Star Rating'] == 3:
                df.at[index, 'Response'] = 'Thanks for the neutral feedback, please let us know in case of any issues. Thanks, BOI'

            else:
                df.at[index, 'Response'] = 'Sorry to hear, Please help us understand this issue you are facing in depth by writing it to BOIMobileSupport@bankofindia.co.in. We will look into this with priority. Thank you, BOI team.'


    return df
