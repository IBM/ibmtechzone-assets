Description:
This asset facilitates to evaluate predictions made using LLM to get accuracy and save false predictions to Excel.

Instructions for Use:
Ensure the .env file is located in the same directory, then execute the "evaluation_app.py" python file.

Explanation:
Each comment explains functionality of corresponding content.
"main" function is used to evaluate predictions and save false predictions to Excel.

"main" function:
1. Reads the testing dataset from 'test.csv' containing 'review_text' and 'issue_ground_truth' columns.
2. Adds a new column 'predicted_issue' to store predictions.
3. Identifies false predictions using a custom function.
4. Calculates accuracy of the classification.
5. Prints the calculated accuracy.
6. Saves false predictions into an Excel file.

Requires 'false_prediction_identification', 'get_accuracy', and 'false_predictions_into_excel', "watson_x" modules.
'false_prediction_identification.py' file identifies false predictions.
'get_accuracy.py' file computes accuracy based on true positives.
'false_predictions_into_excel.py' file saves false predictions to Excel.
'watson_x.py' file is used to the prediction based on review in testing dataset.