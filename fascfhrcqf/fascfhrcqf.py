import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import json
import numpy as np
from pydub import AudioSegment
import subprocess
from dotenv import load_dotenv
import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

load_dotenv()

SERVICE_URL=os.getenv("STT_SERVICE_URL")
API_KEY_S2T = os.getenv("API_KEY_S2T")
authenticator = IAMAuthenticator(API_KEY_S2T)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(SERVICE_URL)

file_path_video = "sample.mp4"
file_path = 'input_audio.wav'

api_key = os.getenv("IBM_CLOUD_API_KEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("PROJECT_ID", None)

def transcribe_audio(audio_data):
    audio_file_path = audio_data["audio_path"]
    print("Started:- ", audio_file_path)
    json_output = f"""{audio_file_path.split(".")[0]}.json"""
    
    with open(audio_file_path, 'rb') as audio_file:
        speech_recognition_results = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/wav',
            word_alternatives_threshold=0.9,
            speaker_labels=True,
        ).get_result()
    
    audio_data["text"] = speech_recognition_results
    timeFrame = []
    for d in speech_recognition_results["results"]:
        timeFrame.append(pd.DataFrame(data=d["alternatives"][0]["timestamps"],columns=["word","start","end"]))
    timeFrame = pd.concat(timeFrame).reset_index(drop=True)
    timeFrame["start"] = timeFrame["start"]+audio_data["start_time"]
    timeFrame["end"] = timeFrame["end"]+audio_data["start_time"]
    
    print("Dumping to:- ", json_output)
    with open(json_output, 'w') as f:
        json.dump(speech_recognition_results, f)
    return timeFrame
def get_wml_creds():
    if api_key is None or ibm_cloud_url is None or project_id is None:
        print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
    else:
        creds = {
            "url": ibm_cloud_url,
            "apikey": api_key 
        }
    return project_id, creds
project_id, creds = get_wml_creds()

def calling_watsonx(prompt):
    params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 300,
            GenParams.TEMPERATURE: 0,
        }
    model = Model(model_id='meta-llama/llama-2-70b-chat', params=params, credentials=creds, project_id=project_id)  
    response = model.generate_text(prompt)
    return response

def runFFmpeg(commands):
    if subprocess.run(commands.split(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode != 0:
        print ("There was an error running your FFmpeg script")

def get_duration_pydub(file_path):
   audio_file = AudioSegment.from_file(file_path)
   duration = audio_file.duration_seconds
   return duration

print("Converting video to wav")
runFFmpeg(f"""ffmpeg -i {file_path_video} {file_path}""")
duration = get_duration_pydub(file_path)
print("Length of the video:- ",duration)

batch = 540  ## seconds
start_time = 0
i = 0 
audioData = []
print("############ GENERATE TRANSCRIPT #####################")
while (duration>0):
    path = f"""audio/{i}.wav"""
    cmd = f"""ffmpeg -ss {start_time} -i input_audio.wav -t {batch} {path} -y"""
    audioData.append({"start_time":start_time, "end_time": start_time+(duration if duration-batch<0 else batch), "audio_path":path})
    runFFmpeg(cmd)
    print(start_time, start_time+(duration if duration-batch<0 else batch))
    i+=1
    start_time = start_time+(duration if duration-batch<0 else batch)
    duration-=batch

output = Parallel(n_jobs=5)(delayed(transcribe_audio)(d) for d in audioData)
output = pd.concat(output).sort_values(by=["start"])
output.to_csv("input.csv",index=False)

data = pd.read_csv("input.csv")
time_gap = 3
start_time = 0
end_time = data["start"].values[-1]
inputs =[]
timestamps = []
print("############# CREATE TIMESTAMP #####################")
while (start_time<end_time):
    df = data[(data["start"]>(start_time)) & (data["start"]<(start_time+time_gap)) ]
    start_min = f"""{start_time//60}:{start_time%60}"""
    end_min = f"""{(start_time+time_gap)//60}:{(start_time+time_gap)%60}"""
    timestamps.append(end_min)
    input_text = " ".join(df["word"].values.tolist())
    inputs.append(input_text)
    start_time+=time_gap
    print("TimeStamp:- ", end_min)
    print("Input:- ", input_text)

transcript_df = pd.DataFrame()
transcript_df["timestamp"]= timestamps
transcript_df["transcript"]= inputs
response=[]
prompts = []
print("############# CLASSIFY HIGHLIGHTS #####################")
for i in tqdm(range(transcript_df.shape[0])):
    row = transcript_df.loc[i]
    input_text = row["transcript"]
    prompt=f"""[INST] <<SYS>>
You are a helpful, respectful and honest assistant. User will provide transcript. You will need to analyse the transcript and answer the given transcript can be used for highlight or not. Output should have only highlight or not highlight. No explanation required.
<</SYS>>

Classify the given text in triple backtick as highlight or not highlight.

```{input_text}```[/INST]"""
    
    output = calling_watsonx(prompt)
    response.append(output)
    prompts.append(prompt)
    print("TimeStamp:- ", row["timestamp"])
    print("Input:- ", input_text)
    print("Response:- ", output)

transcript_df["output"]=response
transcript_df["prompt"]=prompts
transcript_df["output"] = transcript_df["output"].apply(lambda x : "not highlight" if "not highlight" in x.lower() else "highlight")
transcript_df.to_csv("output.csv",index=False)
fig, ax = plt.subplots(figsize=(50,4))
sns.heatmap(transcript_df.set_index("timestamp")["output"].map({"highlight":1,"not highlight":0}).reset_index().set_index("timestamp").T, ax=ax)
plt.savefig("image.jpeg")