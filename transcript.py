from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from typing import List

# Supported languages for transcript extraction
available_languages = ['en', 'tr', 'de', 'fr', 'es']

def transcript_from_youtubeloader(url: str) -> List:
    """
    Extracts the transcript from the YouTube URL using YoutubeLoader.

    Args:
        url (str): The YouTube video URL.

    Returns:
        List: A list of Langchain Document objects extracted from the video.
    """
    loader = YoutubeLoader.from_youtube_url(
        url,
        add_video_info=False,
        transcript_format=TranscriptFormat.CHUNKS,
        chunk_size_seconds=15,
        language=available_languages
    )
    docs = loader.load()
    return docs

def transcript_with_whisper():
    pass