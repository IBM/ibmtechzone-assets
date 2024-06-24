import pandas as pd
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize

# Ensure you have NLTK downloaded
import nltk
nltk.download('punkt')

def load_data(file_path, text_column, label_column):
    """
    Load data from a CSV file.
    :param file_path: Path to the CSV file
    :param text_column: Name of the column containing the text data
    :param label_column: Name of the column containing the label data
    :return: DataFrame with text and label columns
    """
    df = pd.read_csv(file_path)
    return df[[text_column, label_column]]

def check_and_convert_data_types(df, text_column, label_column):
    """
    Check and convert the data types of the text and label columns.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    :param label_column: Name of the column containing the label data
    """
    try:
        # Ensure text column is of string type
        if pd.api.types.is_string_dtype(df[text_column]):
            print(f"{text_column} is already of string type.")
        else:
            df[text_column] = df[text_column].astype(str)
            print(f"Converted {text_column} to string type.")
    except Exception as e:
        print(f"Error converting {text_column} to string type: {e}")

    try:
        # Ensure label column is of categorical or object type
        if pd.api.types.is_categorical_dtype(df[label_column]) or pd.api.types.is_object_dtype(df[label_column]):
            print(f"{label_column} is already of categorical or object type.")
        else:
            df[label_column] = df[label_column].astype('category')
            print(f"Converted {label_column} to categorical type.")
    except Exception as e:
        print(f"Error converting {label_column} to categorical type: {e}")

def clean_data(df, text_column, label_column):
    """
    Clean the dataset by handling null values and converting them to proper NaN.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    :param label_column: Name of the column containing the label data
    """
    null_values = ["null", "None", "", " "]
    df[text_column].replace(null_values, pd.NA, inplace=True)
    df[label_column].replace(null_values, pd.NA, inplace=True)
    df.dropna(subset=[text_column, label_column], inplace=True)

def check_data_size(df):
    """
    Check the size of the dataset.
    :param df: DataFrame containing the dataset
    """
    print(f"Dataset contains {len(df)} samples.")

def check_missing_data(df, text_column, label_column):
    """
    Check for missing data in the dataset.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    :param label_column: Name of the column containing the label data
    """
    missing_text = df[text_column].isnull().sum()
    missing_labels = df[label_column].isnull().sum()
    print(f"Missing text data: {missing_text}")
    print(f"Missing label data: {missing_labels}")

def check_class_balance(df, label_column):
    """
    Check the balance of classes in the dataset.
    :param df: DataFrame containing the dataset
    :param label_column: Name of the column containing the label data
    """
    class_counts = df[label_column].value_counts()
    print("Class distribution:")
    print(class_counts)
    
    class_counts.plot(kind='bar')
    plt.xlabel('Class')
    plt.ylabel('Frequency')
    plt.title('Class Distribution')
    plt.show()

def analyze_text_length(df, text_column):
    """
    Analyze the length of the text data.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    """
    df['text_length'] = df[text_column].apply(lambda x: len(word_tokenize(x)))
    print(df['text_length'].describe())
    
    plt.hist(df['text_length'], bins=30)
    plt.title('Text Length Distribution')
    plt.xlabel('Number of words')
    plt.ylabel('Frequency')
    plt.show()

def main(file_path, text_column, label_column):
    df = load_data(file_path, text_column, label_column)
    check_and_convert_data_types(df, text_column, label_column)
    clean_data(df, text_column, label_column)
    check_data_size(df)
    check_missing_data(df, text_column, label_column)
    check_class_balance(df, label_column)
    analyze_text_length(df, text_column)

# Example usage
file_path = 'path_to_your_file.csv'
text_column = 'text'
label_column = 'label'
main(file_path, text_column, label_column)
