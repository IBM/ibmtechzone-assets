import os,nltk
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
    
filename=os.environ["filename"]
data=pd.read_csv(filename)
data['summaries']=data['TITLE'] + data['ABSTRACT']
conversations=data['summaries'].values.tolist()
get_topic(conversations)