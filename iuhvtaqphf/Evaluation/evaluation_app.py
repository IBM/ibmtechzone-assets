import pandas as pd
import false_prediction_identification,false_predictions_into_excel, get_accuracy

# Main function to evaluate predictions and save results to Excel.
def main():

    # Reading the testing dataset 
    test_data = pd.read_csv("test.csv")

    # Adding new column to the dataset
    test_data['predicted_issue'] = None

    # To do the prediction and identifying wrongly predicted columns
    false_prediction_index = false_prediction_identification.false_prediction(test_data=test_data)

    # Total correct predictions
    True_positive = len(test_data)-len(false_prediction_index)

    # Evaluation of accuracy
    accuracy = get_accuracy.get_accuracy(test_data, True_positive)
    print('Accuracy of classification is ',accuracy)

    # To save the False prediction into a excel.
    false_predictions_into_excel.false_prediction_data(false_prediction_index,test_data)

# Entry point of the script
if __name__ == "__main__":
	main()
