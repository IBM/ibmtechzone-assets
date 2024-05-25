import os
HF_TOKEN = os.environ["hf_token"]

!huggingface-cli login --token "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"

# Import required libraries
import json
import numpy as np
import torch, torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, WhisperTimeStampLogitsProcessor
from transformers.pipelines.audio_utils import ffmpeg_read
from pyannote.audio import Pipeline
import subprocess
subprocess.run(['wget', '-O', 'demo.wav', 'https://docs.google.com/uc?export=download&id=1CaAJoA6N52NSeBZJC2A2DDZj1tz62aJl'], check=True)
print(f"Sample File Downloaded Successfully.\n")
audio_file_path = os.path.abspath("demo.wav")



# Utility functions to convert ASR output to VTT or SRT file format for Captioning task
def chunks_to_vtt(chunks):
    vtt_content = "WEBVTT\n\n"
    for idx, chunk in enumerate(chunks):
        start_time = chunk["timestamp"][0]
        end_time = chunk["timestamp"][1]
        text = chunk["text"].strip()
        vtt_content += f"{idx+1}\n"  # optional
        vtt_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
        vtt_content += f"{text}\n\n"
    return vtt_content

def format_time(seconds):
    hours = int(seconds / 3600)
    seconds %= 3600
    minutes = int(seconds / 60)
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02}.{milliseconds:03}"

def convert_to_srt(chunks):
    srt_content = ''
    for i, chunk in enumerate(chunks, start=1):
        start_time = chunk['timestamp'][0]
        end_time = chunk['timestamp'][1]
        text = chunk['text'].strip()
        srt_content += f"{i}\n"
        srt_content += f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
        srt_content += f"{text}\n\n"
    return srt_content

def format_srt_time(seconds):
    milliseconds = int(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds = milliseconds / 1000
    return "{:02d}:{:02d}:{:06.3f}".format(hours, minutes, seconds)



# Setup the device and datatype 
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
print(f"Using Device: {device} with DataType: {torch_dtype}")



# Speech Recognition Pipeline - returns utterance-level transcriptions and corresponding timestamps
model_id = "openai/whisper-large-v3"
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True).to(device)
processor = AutoProcessor.from_pretrained(model_id)
asr_pipeline = pipeline(
    task="automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    stride_length_s=5,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
    generate_kwargs={"language": "english"}
)



# Speaker Diarization Pipeline - returns speaker timelines i.e., timestamps for 'which speaker spoke when'
diarization_pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=True).to(device)



# Load the sample downloaded audio file
waveform, sample_rate = torchaudio.load(audio_file_path)
print("Audio Sampling Rate:", sample_rate)
print("Audio Waveform Shape:", waveform.shape)



# Run the ASR pipeline and get the end timestamps for each chunk from the ASR output
print("Running the ASR Pipeline....")
asr_output = asr_pipeline(audio_file_path)
print("Obtained Transcript:" , asr_output["text"])
transcript = asr_output["chunks"]
end_timestamps = np.array([chunk["timestamp"][-1] for chunk in transcript]) 



# Convert chunks to VTT & SRT format
vtt_content = chunks_to_vtt(transcript)
with open("demo_output.vtt", "w") as f:
    f.write(vtt_content)

srt_content = convert_to_srt(transcript)
with open("demo_output.srt", "w") as f:
    f.write(srt_content)

print("Saved the VTT and SRT files with utterance-level transcriptions and their corresponding timestamps!")



# Utility function to preprocess the audio with desired sampling rate
def preprocess(inputs, sample_rate):
    if isinstance(inputs, str):
        with open(inputs, "rb") as f:
            inputs = f.read()
    if isinstance(inputs, bytes):
        inputs = ffmpeg_read(bpayload=inputs, sampling_rate=sample_rate)
    if not isinstance(inputs, np.ndarray):
        raise ValueError(f"We expect a numpy ndarray as input, got `{type(inputs)}`")
    if len(inputs.shape) != 1:
        raise ValueError("We expect a single channel audio input for ASRDiarizePipeline")
    # diarization model expects float32 torch tensor of shape `(channels, seq_len)`
    diarizer_inputs = torch.from_numpy(inputs).float()
    diarizer_inputs = diarizer_inputs.unsqueeze(0)
    return inputs, diarizer_inputs



# Run the speaker diarization pipeline
print("Running the Speaker Diarization Pipeline....")
inputs, diarizer_inputs = preprocess(audio_file_path, sample_rate)
diarization = diarization_pipeline({"waveform": diarizer_inputs , "sample_rate": sample_rate}, min_speakers=1, max_speakers=3)
segments = []
for segment, track, label in diarization.itertracks(yield_label=True):
    segments.append({
        'segment': {
            'start': segment.start,
            'end': segment.end
        },
        'track': track,
        'label': label
    })

# diarizer output may contain consecutive segments from the same speaker (e.g. {(0 -> 1, speaker_1), (1 -> 1.5, speaker_1), ...})
# we combine these segments to give overall timestamps for each speaker's turn (e.g. {(0 -> 1.5, speaker_1), ...})
new_segments = []
prev_segment = cur_segment = segments[0]

for i in range(1, len(segments)):
    cur_segment = segments[i]
    # check if we have changed speaker ("label")
    if cur_segment["label"] != prev_segment["label"] and i < len(segments):
        # add the start/end times for the super-segment to the new list
        new_segments.append({
            "segment": {
                "start": prev_segment["segment"]["start"],
                "end": cur_segment["segment"]["start"]
            },
            "speaker": prev_segment["label"],
        })
        prev_segment = segments[i]

# add the last segment(s) if there was no speaker change
new_segments.append({
    "segment": {
        "start": prev_segment["segment"]["start"],
        "end": cur_segment["segment"]["end"]
    },
    "speaker": prev_segment["label"],
})

# align the diarizer timestamps and the ASR timestamps
segmented_preds = []
group_by_speaker = True

for segment in new_segments:
    end_time = segment["segment"]["end"]
    # find the ASR end timestamp that is closest to the diarizer's end timestamp and cut the transcript to here
    upto_idx = np.argmin(np.abs(end_timestamps - end_time))

    if group_by_speaker:
        segmented_preds.append({
            "speaker":
            segment["speaker"],
            "text":
            "".join([chunk["text"] for chunk in transcript[:upto_idx + 1]]),
            "timestamp": (transcript[0]["timestamp"][0], transcript[upto_idx]["timestamp"][1]),
        })
    else:
        for i in range(upto_idx + 1):
            segmented_preds.append({"speaker": segment["speaker"], **transcript[i]})

    # crop the transcripts and timestamp lists according to the latest timestamp (for faster argmin)
    transcript = transcript[upto_idx + 1:]
    end_timestamps = end_timestamps[upto_idx + 1:]

print("Obtained results from Automatic Speech Recognition with Speaker Diarization based on open-source Whisper model:\n")
print(json.dumps(segmented_preds, ensure_ascii=False, indent=2))