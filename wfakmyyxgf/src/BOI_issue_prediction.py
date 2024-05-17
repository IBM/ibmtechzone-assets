import pandas as pd
from utils import issue_prediction


# To make the issue prediction
def boi_prediction(test_data):

    # Adding new column to the dataset
    test_data['predicted_issue'] = None
    # print("length : ",len(test_data))
    # print(test_data)

    # To do the prediction and identifying wrongly predicted columns
    # predicted_issue_data, issue_list = issue_prediction.issue_prediction(test_data)
    predicted_issue_data, issue_list = issue_prediction.issue_prediction(test_data)
    return predicted_issue_data, issue_list
