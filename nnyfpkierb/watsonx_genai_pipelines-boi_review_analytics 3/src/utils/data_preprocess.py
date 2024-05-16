import re
import pandas as pd
import nltk
from nltk.corpus import words

nltk.download('words')

# Set of common English words
english_words = set(words.words())

def preprocessing(file_name):

    df = pd.read_excel(file_name)
    # print(df.head())
    # print("data after preprocessing")

    df = df.dropna(subset='Review Text')

    # Function to detect special emojis and Hindi text
    def detect_special_characters(text):
        # Define patterns for emojis and Hindi characters

        emoji_pattern = re.compile("["
                                "\U0001F600-\U0001F64F"  # Emoticons
                                "\U0001F300-\U0001F5FF"  # Symbols & pictographs
                                "\u274C"  # Few symbols
                                "\U0001F680-\U0001F6FF"  # Transport & map symbols
                                "\U0001F700-\U0001F77F"  # Alphabetic presentation forms
                                "\U0001F780-\U0001F7FF"  # Geometric shapes
                                "\U0001F800-\U0001F8FF"  # Variable selectors
                                "\U0001F900-\U0001F9FF"  # Supplemental private use area-A
                                "\U0001FA00-\U0001FA6F"  # Supplemental private use area-B
                                "\U0001FA70-\U0001FAFF"  # Supplemental private use area-C
                                "\U0001F000-\U0001FFFF"  # Miscellaneous symbols
                                "\u0900-\u097F"  # Devanagari (Hindi)
                                "\u0B80-\u0BFF"  # Tamil
                                "\u0C00-\u0C7F"  # Telugu
                                "\u0C80-\u0CFF"  # Kannada
                                "\u0A80-\u0AFF"  # Gujarati
                                "#"
                                "]+", flags=re.UNICODE)

        return bool(emoji_pattern.search(text))

    # Apply the function to detect special characters and create a boolean mask
    mask = df["Review Text"].apply(detect_special_characters)

    # Extract rows with special emojis or Hindi text
    result_df = df[mask]

    row_to_be_dropped = [result_df.iloc[num].name for num in range(len(result_df))]

    # Dropping the rows which has any emoji or Hindi text.
    df = df.drop(index=row_to_be_dropped).reset_index(drop=True)
 
    def is_meaningful_english(text):
    # Tokenize the text into words
        words_in_text = nltk.word_tokenize(text.lower())
        
        # Count the number of words in the text
        total_words = len(words_in_text)
        # print(text)
        # Count the number of common English words in the text
        english_word_count = sum(word in english_words for word in words_in_text)
        
        # Calculate the ratio of common English words
        ratio = english_word_count / total_words
        
        # If the ratio is above a certain threshold, consider it as meaningful English text
        return ratio > 0.45  # You can adjust the threshold as needed

    df = df[df['Review Text'].apply(is_meaningful_english)]

    # Resetting the indexes after droping the rows.
    df.reset_index(drop=True, inplace=True)

    return df