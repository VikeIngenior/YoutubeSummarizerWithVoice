from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat

def transcript_from_youtubeloader(url: str):
    loader = YoutubeLoader.from_youtube_url(
        url,
        add_video_info=False,
        transcript_format=TranscriptFormat.CHUNKS,
        chunk_size_seconds=15,
        language=['tr']
    )
    docs = loader.load()
    print(docs[1])
    return docs

def transcript_with_whisper():
    pass