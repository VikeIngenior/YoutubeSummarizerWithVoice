from pathlib import Path
from openai import OpenAI

speech_file_path = Path(__file__).parent / 'speech.mp3'
def voiceover(summary: str, api_key: str) -> Path:
    """
    Generates a voiceover from the given text summary using a text-to-speech model.

    This function calls the TTS model with a specified voice and converts
    the given text into speech. The generated speech is saved to a file.

    --> Refer to OpenAI text-to-speech model documentation
    to see more about models and different voices

    Args:
        summary (str): The summary to be converted into speech.
        api_key (str): The API key to use for TTS.
    Returns:
        str: The file path where the generated speech is saved.
    """
    client = OpenAI(api_key=api_key)

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=summary
    )

    response.write_to_file(speech_file_path)
    return speech_file_path