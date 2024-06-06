from pydub import AudioSegment
import os
def audio_to_wav(input_file, output_folder):
    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension == ".m4a":
        format_type = "m4a"
    elif file_extension == ".mp3":
        format_type = "mp3"
    else:
        raise ValueError("Unsupported file format: {}".format(file_extension))
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format=format_type)
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    # Create the output file path
    filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, filename + ".wav")
    # Export the audio to WAV format
    audio.export(output_file, format="wav")
    return output_file
# Example usage
# audio_to_wav("example.m4a", "output_folder")
# audio_to_wav("example.mp3", "output_folder")