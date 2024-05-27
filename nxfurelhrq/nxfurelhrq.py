from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_watson import ApiException
import pandas as pd

def generate_sentiment_for_speakers(df):
    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(URL OF NLU)

    speakers_sentiment_scores = {}
    final_transcript_for_sentiment=""
    speaker_list =[]
    Sentence_list=[]
    sentiment_score_list=[]
    start_time_list=[]
    end_time_list=[]
    # Iterate through each sentence and speaker
    for index, row in df.iterrows():
        temp={}
        speaker = row['Speaker']
        sentence = row['Transcript']
        start_time = row["Start Time"]
        end_time = row['End Time']

        try:
            response = natural_language_understanding.analyze(
            text=sentence.strip(),
            features=Features(sentiment=SentimentOptions())
        ).get_result()
            
            sentiment_score = response['sentiment']['document']['score']
            final_transcript_for_sentiment += sentence
            final_transcript_for_sentiment += "/n"

            speaker_list.append(speaker)
            Sentence_list.append(sentence)
            sentiment_score_list.append(sentiment_score)
            start_time_list.append(start_time)
            end_time_list.append(end_time)

            if speaker not in speakers_sentiment_scores:
                speakers_sentiment_scores[speaker] = 0.0
                speakers_sentiment_scores[speaker] += sentiment_score
            
        except ApiException as ex:
            print("Method failed with status code " + str(ex.code) + ": " + ex.message)


    speaker_sentiments_for_each_line_df = pd.DataFrame({"Speaker": speaker_list, "Transcript": Sentence_list,"Start Time": start_time_list,"End Time":end_time_list, "Sentiment Score":sentiment_score_list})
    # Generate sentiment for entire transcript
    try:
        response = natural_language_understanding.analyze(
        text=sentence.strip(),
        features=Features(sentiment=SentimentOptions())
    ).get_result()
        sentiment_score_for_transcript = response['sentiment']['document']['score']
    except ApiException as ex:
        print("Method failed with status code " + str(ex.code) + ": " + ex.message)
    
    return speaker_sentiments_for_each_line_df,speakers_sentiment_scores, sentiment_score_for_transcript


df = pd.read_csv(csv file path)
speaker_sentiments_for_each_line_df,speakers_sentiment_scores, sentiment_score_for_transcript = generate_sentiment_for_speakers(df) # generate sentiment for each speaker and transcript
speaker_sentiments_for_each_line_df.to_csv("FinalSheetWithSentimentScore.csv")