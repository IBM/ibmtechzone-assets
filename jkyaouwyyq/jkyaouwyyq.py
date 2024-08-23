from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv
load_dotenv()
import os,requests,zipfile



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
print("file_name ",file_name)
print("file_path ",file_path)
# Write the downloaded content to a file
with open(file_path, 'wb') as file:
    file.write(response.content)
print("file ",file)
# Iterate through all files in the current working directory
for file in os.listdir(CWD):
    if file.endswith('.zip'):
        # Unzip the file
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(CWD)

# Replace these with your instance details
api_key = os.getenv('api_key')  # e.g., dev1345.service-now.com
url = os.getenv('url')

# mp4_file =  "Vidnoz.mp4"
wav_file = "output_audio.wav"
audio_type = "audio/wav"

def convert_mp4_wav(mp4_file, wav_file):
    try:
        video_clip = VideoFileClip(mp4_file)
        # print(11)
        audio_clip = video_clip.audio
        # print(22)
        audio_clip.write_audiofile(wav_file)
        audio_clip.close()
        video_clip.close()
        print("convert_mp4_wav")
        return 1
    except Exception as e:
        print(e)
        return 0

def convert_speech_text(wav_file,audio_type,api_key,url):
    try:
        authenticator = IAMAuthenticator(api_key)
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_service_url(url)
        with open(wav_file, 'rb') as audio_file:
            response = speech_to_text.recognize(
                audio=audio_file,
                content_type=audio_type,
                model=  'en-US_Telephony',
            ).get_result()
        return response
    except Exception as e:
        print(e)
        return ""
    
def get_transcript(mp4_file, wav_file,audio_type,api_key,url):
    try:
        op =  convert_mp4_wav(mp4_file, wav_file)
        op = 1
        # print("op",op)
        if op == 1 :
            data = convert_speech_text(wav_file,audio_type,api_key,url)
            # print("data")
            # print(data)
            transcripts = [result['alternatives'][0]['transcript'] for result in data['results']]
            combined_transcript = ' '.join(transcripts)
            print(combined_transcript)
            with open('output.txt', 'w') as f:
                f.write(combined_transcript)
            return "Transcript Generated."
        else:
            return "Not Generated."
    except Exception as e:
        print(e)
        return "Not Generated."
    

print(get_transcript(file, wav_file,audio_type,api_key,url))
