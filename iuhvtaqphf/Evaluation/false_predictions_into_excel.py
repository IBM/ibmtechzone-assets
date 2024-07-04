import pandas as pd

# Function to save false predictions in excel
def false_prediction_data(false_prediction_index, test_data):
    false_predicted_rows = pd.DataFrame()
    false_predicted_rows = test_data.iloc[false_prediction_index].copy()
    false_predicted_rows.to_excel('False_Predictions.xlsx', index = False) 
