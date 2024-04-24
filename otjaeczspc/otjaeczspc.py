import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Join tokens back into a string
    processed_text = ' '.join(filtered_tokens)
    
    return processed_text

# Read the CSV file
df = pd.read_csv('your_dataset.csv')

# Preprocess the 'text' column
df['processed_text'] = df['text'].apply(preprocess_text)

# Save the preprocessed data back to CSV
df.to_csv('preprocessed_dataset.csv', index=False)

print("Text data preprocessing is completed!")
