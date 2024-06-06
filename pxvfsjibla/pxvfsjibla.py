def call_speech_to_text(audio_file_path,audio_type):
    api_key = ''
    url = ''
    authenticator = IAMAuthenticator(api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(url)
    with open(audio_file_path, 'rb') as audio_file:
        response = speech_to_text.recognize(
            audio=audio_file,
            content_type=audio_type,
            timestamps=True,
            speaker_labels=True,
            model='en-US_Telephony_LSM', #en-IN_Telephony',
            redaction=True,
            background_audio_suppression=0.5,
            end_of_phrase_silence_time =1.0,
            speech_detector_sensitivity=0.55,
            smart_formatting=True,
            smart_formatting_version=2,
            profanity_filter=True
        ).get_result()
    return response
    
