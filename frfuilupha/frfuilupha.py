import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage

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
    try:
        df = pd.read_csv(file_path)
        if text_column not in df.columns or label_column not in df.columns:
            raise ValueError(f"Columns '{text_column}' or '{label_column}' not found in the dataset.")
        return df[[text_column, label_column]]
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def preprocess_text(text):
    """
    Preprocess the text data.
    :param text: String of text data
    :return: Preprocessed text data
    """
    text = text.lower()  # Convert text to lowercase
    text = ' '.join(word_tokenize(text))  # Tokenize text
    return text

def plot_word_cloud(df, text_column):
    """
    Generate and plot a word cloud of the text data.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    """
    try:
        # Concatenate all texts into a single string
        all_texts = ' '.join(df[text_column].apply(preprocess_text))

        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_texts)

        # Plot word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud')
        plt.show()
    except Exception as e:
        print(f"Error plotting word cloud: {e}")

def plot_word_frequency(df, text_column):
    """
    Plot the word frequency distribution of the text data.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    """
    try:
        # Preprocess text data and tokenize
        df[text_column] = df[text_column].apply(preprocess_text)

        # Tokenize and calculate word frequencies
        all_words = ' '.join(df[text_column].tolist())
        tokens = word_tokenize(all_words)
        word_freq = pd.Series(tokens).value_counts()[:30]

        # Plot word frequency distribution
        word_freq.plot(kind='bar', figsize=(12, 6))
        plt.title('Top 30 Most Frequent Words')
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.show()
    except Exception as e:
        print(f"Error plotting word frequency distribution: {e}")

def plot_text_similarity(df, text_column):
    """
    Plot a heatmap of text similarity using cosine similarity.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    """
    try:
        # Preprocess text data
        df[text_column] = df[text_column].apply(preprocess_text)

        # Vectorize text data
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df[text_column])

        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Plot heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(similarity_matrix, cmap='viridis', interpolation='nearest')
        plt.colorbar()
        plt.title('Text Similarity Heatmap')
        plt.show()
    except Exception as e:
        print(f"Error plotting text similarity heatmap: {e}")

def plot_label_clustering(df, text_column, label_column):
    """
    Perform hierarchical clustering on the class labels based on text similarity.
    :param df: DataFrame containing the dataset
    :param text_column: Name of the column containing the text data
    :param label_column: Name of the column containing the label data
    """
    try:
        # Preprocess text data
        df[text_column] = df[text_column].apply(preprocess_text)

        # Vectorize text data
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df[text_column])

        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Perform hierarchical clustering
        linkage_matrix = linkage(similarity_matrix, method='ward')

        # Plot dendrogram
        plt.figure(figsize=(12, 8))
        dendrogram(linkage_matrix, labels=df[label_column].tolist(), orientation='top', leaf_font_size=10)
        plt.title('Hierarchical Clustering of Class Labels')
        plt.xlabel('Class Labels')
        plt.ylabel('Distance')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting label clustering dendrogram: {e}")

def main(file_path, text_column, label_column):
    """
    Main function to execute the visualization steps.
    :param file_path: Path to the CSV file
    :param text_column: Name of the column containing the text data
    :param label_column: Name of the column containing the label data
    """
    # Load data
    df = load_data(file_path, text_column, label_column)
    if df is None:
        return
    
    # Plot word cloud
    plot_word_cloud(df, text_column)
    
    # Plot word frequency distribution
    plot_word_frequency(df, text_column)
    
    # Plot text similarity heatmap
    plot_text_similarity(df, text_column)
    
    # Plot label clustering dendrogram
    plot_label_clustering(df, text_column, label_column)

# Example usage
file_path = 'path_to_your_file.csv'
text_column = 'text'
label_column = 'label'
main(file_path, text_column, label_column)
