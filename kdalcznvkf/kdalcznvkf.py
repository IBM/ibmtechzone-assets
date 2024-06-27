import os,nltk
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
ntlk.download('stopwords')
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
    texts=conversations.split("\n") 

    vectorizer_model = CountVectorizer(ngram_range=(1,3),stop_words='stopword')

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
    topics, probs = model.fit_transform(texts)
    print(topics)
    print(model.get_topics())
    df=model.get_topic_info().head(7).set_index('Topic')[['Count', 'Name', 'Representation']]
    df.to_csv("./topics_on_prompt_summary.csv")
    
conversations=os.environ["bert_topic_asset"]
get_topic(conversations)