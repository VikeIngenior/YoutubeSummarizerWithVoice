from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from langchain.chains.combine_documents import create_stuff_documents_chain
from constants import FIRST_PERSON_PROMPT, THIRD_PERSON_PROMPT
import streamlit as st
from pathlib import Path
import re
from typing import List
from openai import OpenAI

speech_file_path = Path(__file__).parent / 'speech.mp3'

class Video:
    def __init__(self, url: str):
        self.url = url
        self.available_languages = ['en', 'tr', 'de', 'fr', 'es']
        self.summary_type = "Third-Person"
        self.summary_length = "Short"
        self.transcript = None
        self.summary = None
        self.audio = None


    def get_transcript(self) -> List | None:
        """
        Retrieves the transcript of the YouTube video in chunks.

        This function uses `YoutubeLoader` to fetch the transcript of the video.
        The transcript is divided into chunks of 15 seconds.
        The function attempts to load the transcript in one of the available languages
        specified in `self.available_languages`.

        Returns:
            List | None: A list of transcript chunks if successful, otherwise None.
        """
        loader = YoutubeLoader.from_youtube_url(
            youtube_url= self.url,
            add_video_info=False,
            transcript_format=TranscriptFormat.CHUNKS,
            chunk_size_seconds=15,
            language=self.available_languages,
        )
        try:
            self.transcript = loader.load()
            return self.transcript
        except:
            return None

    def get_summary(self, llm, prompt_type: str, length: str, language: str) -> str | None:
        """
        Summarizes the transcript using an LLM model.

        Args:
            llm: The language model instance used for summarization.
            prompt_type (str): Type of summary ('First-Person' or 'Third-Person').
            length (str): Length of summary ('Short' or 'Long').
            language (str): Output language of the summary.
        Returns:
            str: The summarized text if successful, otherwise None.
        """
        summary_type = {"First-Person": FIRST_PERSON_PROMPT, "Third-Person": THIRD_PERSON_PROMPT}
        summary_length = {"Short": 2, "Long": 7}

        self.summary_type = summary_type.get(prompt_type)
        self.summary_length = summary_length.get(length)

        if llm is not None:  # If there is an API key for the selected model.
            try:
                chain = create_stuff_documents_chain(llm, self.summary_type)
                result = chain.invoke({"context": self.transcript, "length": self.summary_length, "language": language})
                #return result
                self.summary = result
                return result
            except Exception as e:
                match = re.search(r"'message': '([^']*)'", str(e))
                error_message = match.group(
                    1) if match else "Unknown Error! (Probably the balance is too low for the API Key.)"
                st.error(error_message)
                return None

    def voiceover(self, api_key: str) -> Path:
        """
        Generates a voiceover from the given text summary using a text-to-speech model.

        This function calls the TTS model with a specified voice and converts
        the given text into speech. The generated speech is saved to a file.

        --> Refer to OpenAI text-to-speech model documentation
        to see more about models and different voices

        Args:
            api_key (str): The API key to use for TTS.
        Returns:
            Path: The file path where the generated speech is saved.
        """
        client = OpenAI(api_key=api_key)

        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=self.summary
        )

        response.write_to_file(speech_file_path)
        self.audio = speech_file_path
        return speech_file_path
