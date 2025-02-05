from langchain_openai import OpenAIEmbeddings
from YoutubeSummarizerWithVoice.transcript import transcript_from_youtubeloader
from langchain_chroma import Chroma

def initialize_vectorstore(video_url: str):
    """
        Creates a Chroma vectorstore and retriever using the transcript of the video.

        Args:
            video_url (str): YouTube video URL.

        Returns:
            retriever: Chroma retriever instance.
        """

    # Get transcript documents
    docs = transcript_from_youtubeloader(video_url)

    # Initialize vectorstore
    vectorstore = Chroma.from_documents(
        documents=docs,
        collection_name="video-rag",
        embedding=OpenAIEmbeddings(),
        persist_directory="./.chroma"
    )

    # Create retriever
    retriever = Chroma(
        collection_name="video-rag",
        persist_directory="./.chroma",
        embedding_function=OpenAIEmbeddings()
    ).as_retriever()

    return retriever