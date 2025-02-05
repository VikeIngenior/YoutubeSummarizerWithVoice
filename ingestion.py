from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from sympy.physics.units import temperature

from transcript import transcript_from_youtubeloader
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

def get_chain():

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = PromptTemplate.from_template(""" 
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
    Question: {question}
    Context: {context}
    Answer:
    """)

    generation_chain = prompt | llm | StrOutputParser()
    return generation_chain