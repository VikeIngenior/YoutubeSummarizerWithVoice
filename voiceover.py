from pathlib import Path
from openai import OpenAI

client = OpenAI()
speech_file_path = Path(__file__).parent / 'speech.mp3'
def voiceover(summary: str):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=summary
    )

    response.write_to_file(speech_file_path)
    return speech_file_path