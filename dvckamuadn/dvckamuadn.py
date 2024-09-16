import os
import json
from os.path import join, dirname

from pydub import AudioSegment
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Audio segmentation

def trim_audio_into_segments(audio_path, filename, output_folder, segment_duration=120 * 1000):
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        # Empty the output folder if it already contains files
        existing_files = os.listdir(output_folder)
        for file in existing_files:
            file_path = os.path.join(output_folder, file)
            os.remove(file_path)

    total_duration = len(audio)
    duration_in_seconds = len(audio) / 1000  # Convert milliseconds to seconds
    minutes = int(duration_in_seconds // 60)
    seconds = int(duration_in_seconds % 60)
    duration_formatted = f"{minutes}:{seconds:02d}"  # Format seconds with leading zero if needed
    print(f"Audio Duration (in milliseconds)" , duration_formatted)
    segment_number = 0
    segments = []

    # Segment the audio based on 120-second intervals (Use 60-second interval)
    for start_time in range(0, total_duration, segment_duration):
        end_time = min(start_time + segment_duration, total_duration)
        segment = audio[start_time:end_time]

        # Export the segment to a file
        # segment_path = os.path.join(output_folder, f"{segment_number}_segment_{filename}.mp3")
        # segment.export(segment_path, format="mp3")
        segment_path = os.path.join(output_folder, f"{segment_number}_segment_{filename}.wav")
        segment.export(segment_path, format="wav")
        segments.append(segment_path)
        segment_number += 1

    return segments

# 1. Custom Speech-to-Text Model development 

API_KEY = ""
URL = "" # IBM Speech service URL

authenticator = IAMAuthenticator(apikey = API_KEY)
stt_client = SpeechToTextV1(authenticator = authenticator)
stt_client.set_service_url(URL)
# en-US_Multimedia_LSM
language_model = stt_client.create_language_model(
    'example_model',
    'en-US',
    description='First custom language model example'
).get_result()
# print(json.dumps(language_model, indent=2))
customization_id = language_model['customization_id']
customization_id

# List corpora
corpora = stt_client.list_corpora(customization_id).get_result()
print(json.dumps(corpora, indent=2))

# 2. Add a corpus

script_dir = os.getcwd()  # Use current working directory
file_path = os.path.join(script_dir, 'corpus2.txt') # text file with the list of vocabulary (It can include individual words and/or sentences)

with open(file_path, 'rb') as corpus_file:
    stt_client.add_corpus(
        customization_id,
        'corpus1',
        corpus_file,
        allow_overwrite=True
    )

# Check the status of corpus

corpora = stt_client.list_corpora(customization_id).get_result()
print(json.dumps(corpora, indent=2))

######........Keep refresh the above 2 lines until you see the status as 'analyzed' as part of response......#######

# Another way to add new terminology to base STT model
# stt_client.add_words(customization_id, [
#         {   "word": "Toffees", "sounds_like": ["TOFeez"],"display_as":"Toffees"},
#         {   "word": "doucoure", "sounds_like": ["dookoray"], "display_as":"doucoure"}
#         # {   "word":"kirlin", "sounds_like": ["colin", "colon", "call in"], "display_as":"kirlin"}
#         # {   "word":"tate", "sounds_like": ["taten"], "display_as":"tate"},
#         # {   "word":"pay", "sounds_like":["say"], "display_as":"pay"},
#         # {   "word":"quality", "sounds_like":["college"], "display_as":"quality"},
#         # {   "word":"collector", "sounds_like":["corrector"], "display_as":"collector"}
#     ])

# 3. Train custom language model

stt_client.train_language_model(customization_id)
# Poll for language model status.

# Check status of custom language model
language_model = stt_client.get_language_model(customization_id).get_result()
print(json.dumps(language_model, indent=2))

######........Keep refresh the above two lines until you see the status as 'available' as part of response......#######

# 4. Consume custom model for transcript extraction

INPUT_PATH = "Recording 22.wav"
FILENAME = INPUT_PATH.split("/")[-1]
OUTPUT_PATH = "./tts-stt/segments"
segments = trim_audio_into_segments(audio_path=INPUT_PATH, filename=FILENAME, output_folder=OUTPUT_PATH)
for seg in sorted(os.listdir(OUTPUT_PATH)):
    file_path = os.path.join(OUTPUT_PATH , seg)

    with open(file_path , "rb") as audio_file:
        print(f"Getting STT results for {seg}")
        speech_recognition_results = stt_client.recognize(audio = audio_file , model = language_model["base_model_name"] ,base_model_version = language_model["versions"][0], 
                                    language_customization_id=customization_id, customization_weight=0.9, content_type = 'audio/wav', speaker_labels = True,
                                    smart_formatting=True,smart_formatting_version=2,
                                    background_audio_suppression = 0.1, speech_detector_sensitivity = 0.9, split_transcript_at_phrase_end = True
                                    ).get_result()

    combined_transcript = '. '.join(result['alternatives'][0]['transcript'].strip() for result in speech_recognition_results['results'])
    print(combined_transcript)
    with open("transcript.txt", "w", encoding="utf-8") as file:
        file.write(combined_transcript + "\n")