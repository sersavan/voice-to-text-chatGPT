from pydub import AudioSegment
import os
import tempfile
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(file_path, audio_format):
    transcript = ""
    try:
        audio = AudioSegment.from_file(file_path, format=audio_format)

        chunk_length_ms = 30 * 60 * 1000  # 30 minutes in milliseconds
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                chunk.export(temp_file.name, format="mp3")
                with open(temp_file.name, 'rb') as audio_file:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                    transcript_chunk = response.get('text', '') if response else ""
                    transcript += transcript_chunk
            os.remove(temp_file.name)
    except Exception as e:
        print(f"An error occurred: {e}")
    return transcript

def main(speech_file, audio_format):
    full_transcription = transcribe_audio(speech_file)
    summary = create_summary(full_transcription)
    
    with open("transcription.txt", "w") as file:
        file.write(full_transcription)
    
    with open("summary.txt", "w") as file:
        file.write(summary)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe an audio file using OpenAI's Speech-to-Text API, punctiate and roleplay")
    parser.add_argument("path", help="File path for the audio file to be transcribed")
    parser.add_argument("format", help="Audio file format (e.g., 'mp3', 'wav', 'm4a')")
    args = parser.parse_args()

    main(args.path, args.format)
