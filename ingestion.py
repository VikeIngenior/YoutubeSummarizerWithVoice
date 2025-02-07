from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from sympy.physics.units import temperature
from chromadb import PersistentClient
from transcript import transcript_from_youtubeloader
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

def delete_previous_collection(collection_name: str):
    try:
        chroma_client = PersistentClient(path=".chroma")
        chroma_client.delete_collection(collection_name)
    except Exception as e:
        raise Exception(f"Unable to delete collection: {e}")

def initialize_vectorstore(video_url: str):
    """
        Creates a Chroma vectorstore and retriever using the transcript of the video.

        Args:
            video_url (str): YouTube video URL.

        Returns:
            retriever: Chroma retriever instance.
        """

    # Clean the previous collection
    delete_previous_collection("video-rag")

    # Get transcript documents
    docs = transcript_from_youtubeloader(video_url)

    # Initialize vectorstore
    vectorstore = Chroma(
        collection_name="video-rag",
        embedding_function=OpenAIEmbeddings(),
        persist_directory="./.chroma"
    )

    vectorstore.add_documents(docs)

    # Create retriever
    retriever = Chroma(
        collection_name="video-rag",
        persist_directory="./.chroma",
        embedding_function=OpenAIEmbeddings()
    ).as_retriever()

    return retriever

def get_chain(llm):

    llm.temperature=0

    prompt = PromptTemplate.from_template(""" 
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
    Question: {question}
    Context: {context}
    Answer:
    """)

    generation_chain = prompt | llm | StrOutputParser()
    return generation_chain