import os,nltk,requests
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import glob
import os

from sentence_transformers import SentenceTransformer
# from umap import UMAP
# from hdbscan import HDBSCAN

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')



#remove spanish stopwords
stopword=stopwords.words('english')

def get_topic(conversations):

    vectorizer_model = CountVectorizer(ngram_range=(1,3),stop_words='english')

    #Intializing bert model
    model = BERTopic(
        nr_topics=10,
        embedding_model=embedding_model,
        # top_n_words=5,
        vectorizer_model=vectorizer_model,
        language='english', calculate_probabilities=True,
        verbose=True
    )
    # topics, probs = model.fit_transform([response])
    topics, probs = model.fit_transform(conversations)
    print(topics)
    print(model.get_topics())
    df=model.get_topic_info()
    df.to_csv("./topics_on_prompt_summary.csv")


# Define the URL to download
wget_url = os.environ["file_path"]
# Create the 'data' directory if it doesn't exist
os.makedirs('data', exist_ok=True)
# Change the current working directory to 'data'
os.chdir('data')
# Get the current working directory
CWD = os.getcwd()
# Download the file from the URL
response = requests.get(wget_url)
file_name = wget_url.split('/')[-1]
file_path = os.path.join(CWD, file_name)
# Write the downloaded content to a file
with open(file_path, 'wb') as file:
    file.write(response.content)
# Iterate through all files in the current working directory
for file in os.listdir(CWD):
    if file.endswith('.zip'):
        # Unzip the file
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(CWD)
    
filename="data/download"
data=pd.read_csv(filename)
data['summaries']=data['TITLE'] + data['ABSTRACT']
conversations=data['summaries'].values.tolist()
get_topic(conversations)