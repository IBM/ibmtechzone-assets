def process_transcript(transcript_data):
    chat_transcript_list = []
    speaker_list=[]
    combined_data=[]
    chat_transcript = ""
    current_speaker = ""
    current_sentence = ""
    speaker_start_time=[]
    speaker_end_time =[]
    for entry in transcript_data['results']:
        alternatives = entry['alternatives']
        for alternative in alternatives:
            words = alternative['timestamps']
            for word, start_time, end_time in words:
                
                speaker_label = find_speaker_label(transcript_data['speaker_labels'], start_time, end_time)
                if speaker_label != current_speaker:
                    if current_sentence:
                        chat_transcript += f"\nSpeaker {current_speaker}:\n{current_sentence}\n"
                        chat_transcript_list.append(current_sentence)
                        speaker_list.append(f"Speaker {current_speaker}")
                        combined_data.append(f"\nSpeaker {current_speaker}:\n{current_sentence}\n")
                        speaker_start_time.append(current_start_time)
                        speaker_end_time.append(current_end_time)

                    current_speaker = speaker_label
                    current_sentence = word
                    current_start_time = start_time
                    current_end_time = end_time
                else:
                    current_sentence += " " + word
                    current_end_time = end_time
    if current_sentence:
        chat_transcript += f"\nSpeaker {current_speaker}:\n{current_sentence}\n"
        speaker_list.append(f"Speaker {current_speaker}")
        chat_transcript_list.append(current_sentence)
        combined_data.append(f"\nSpeaker {current_speaker}:\n{current_sentence}\n")
        speaker_start_time.append(current_start_time)
        speaker_end_time.append(current_end_time)
    return chat_transcript,chat_transcript_list,speaker_list,combined_data,speaker_start_time,speaker_end_time

def find_speaker_label(speaker_labels, start_time, end_time):
    for label in speaker_labels:
        if label['from'] <= start_time and label['to'] >= end_time:
            return label['speaker']
    return None
