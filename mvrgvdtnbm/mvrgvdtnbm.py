import os
from statistics import mode
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, ClassificationsOptions, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


WATSON_ANALYSER_API_KEY = os.environ["watson_analyser_api_key"]
WATSON_ANALYSER_URL = os.environ["watson_analyser_url"]
TEXT_FOR_ANALYSIS = os.environ["text_for_analysis"]


authenticator = IAMAuthenticator(WATSON_ANALYSER_API_KEY)
nlu = NaturalLanguageUnderstandingV1(version='2019-07-12', authenticator=authenticator)
nlu.set_service_url(WATSON_ANALYSER_URL)


# Performs sentiment analysis: Classify the text into 3 categories - positive, neutral or negative based on its sentiment
def analyze_sentiment(text):
    try:
        # Split the transcript into chunks of 2000 characters
        chunk_size = 2000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        sentiments = []
        
        for chunk in chunks:
            response = nlu.analyze(text=chunk,
                                        features=Features(sentiment=SentimentOptions(document=True)),
                                        language='en').get_result()

            sentiment = response['sentiment']['document']['label']
            sentiments.append(sentiment)
        mode_sentiment = mode(sentiments)
        return mode_sentiment
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")


# Performs tone analysis: It detects seven tones: sad, frustrated, satisfied, excited, polite, impolite, and sympathetic
# For more info: https://cloud.ibm.com/docs/natural-language-understanding?topic=natural-language-understanding-tone_analytics
def analyze_tone(text):
    try:
        # Split the transcript into chunks of 2000 characters
        chunk_size = 2000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        tones = []
        
        for chunk in chunks:
            response = nlu.analyze(text=chunk,
                                        features=Features(classifications=ClassificationsOptions(model="tone-classifications-en-v1")),
                                        language='en').get_result()

            classifications = sorted(response['classifications'], key=lambda x: x["confidence"], reverse=True)
            tone = classifications[0]["class_name"]
            tones.append(tone)

        mode_tone = mode(tones)
        return mode_tone
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")


sentiment_label = analyze_sentiment(TEXT_FOR_ANALYSIS)
tone_label = analyze_tone(TEXT_FOR_ANALYSIS)
print("Sentiment Analysis Result:" , sentiment_label)
print("Tone Analysis Result:" , tone_label)