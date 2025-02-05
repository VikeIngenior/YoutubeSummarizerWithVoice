import streamlit as st
import re
from ingestion import initialize_vectorstore, get_chain
from summarize import summarize_transcript
from transcript import transcript_from_youtubeloader
from voiceover import voiceover
from choose_model import get_available_models, choose_model
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

docs = []

def is_valid_youtube_url(url):
    """
    Checks if the provided URL is a valid YouTube link.

    Args:
        url (str): The URL to be validated.

    Returns:
        bool: True if the URL is a valid YouTube link, False otherwise.
    """
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
    return youtube_pattern.match(url)

def streamlit_interface():
    """
    Streamlit interface for summarizing YouTube videos.

    Users can enter a YouTube video URL, select summarization settings,
    and receive a summary in both text and audio format.
    """
    st.title("Youtube Video Summarizer")
    st.markdown("Type the URL and get the Summary!")

    # Initialize session state keys
    if "video_url" not in st.session_state:
        st.session_state.video_url = ""
    if "summary_type" not in st.session_state:
        st.session_state.summary_type = "Third-Person"
    if "summary_length" not in st.session_state:
        st.session_state.summary_length = "Short"
    if "selected_model" not in st.session_state:
        available_models = list(get_available_models().keys())
        st.session_state.selected_model = available_models[0] if available_models else ""
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "Original Language"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"
    if "summary" not in st.session_state:
        st.session_state.summary = ""
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = ""

    # User input for the URL
    st.session_state.video_url = st.text_input("Enter the URL:", value=st.session_state.video_url)

    # Sidebar settings
    with st.sidebar:
        st.markdown("### Summary Settings")
        st.session_state.summary_type = st.selectbox(
            "Choose the type of the summary:",
            ['First-Person', 'Third-Person'],
            index=0 if st.session_state.summary_type == "First-Person" else 1
        )

        st.session_state.summary_length = st.selectbox(
            "Choose the length of the summary:",
            ['Short', 'Long'],
            index=0 if st.session_state.summary_length == "Short" else 1
        )

        st.markdown("### Choose a Model")
        model_options = list(get_available_models().keys())
        if st.session_state.selected_model not in model_options:
            st.session_state.selected_model = model_options[0] if model_options else ""
        st.session_state.selected_model = st.selectbox(
            "Select a model for summarization:",
            model_options,
            index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
        )
        st.session_state.model = choose_model(st.session_state.selected_model)
        print("MODEL",st.session_state.model)
        # Model Information
        if st.session_state.model is not None:
            model_mapping = {
                "OpenAI GPT-4o": "GPT-4o Mini",
                "Anthropic Claude": "Claude 3 Opus",
                "Google Gemini": "Gemini 1.5 Pro"
            }
            selected_model_info = model_mapping.get(st.session_state.selected_model, "Unknown Model")
            st.info(f"Using **{selected_model_info}** for summarization.")
        else:
            st.warning("No API Key was found for the chosen model!")

        st.markdown("### Choose the Summary Language.")
        language_options = ["Original Language", "English", "Turkish", "Spanish", "French", "German"]
        if st.session_state.selected_language not in language_options:
            st.session_state.selected_language = language_options[0]
        st.session_state.selected_language = st.selectbox(
            "Select the output language:",
            language_options,
            index=language_options.index(st.session_state.selected_language)
        )

    # Summarization button logic
    if st.button("Summarize"):
        if not st.session_state.video_url or (st.session_state.video_url and not is_valid_youtube_url(st.session_state.video_url)):
            st.warning("Please enter a valid URL!")
            return

        with st.spinner("Getting the transcript..."):
            docs = transcript_from_youtubeloader(st.session_state.video_url)

        if not docs:
            st.error("Transcript could not be obtained.")
            return

        with st.spinner("Transcript is being summarized..."):
            st.session_state.summary = summarize_transcript(
                docs,
                st.session_state.summary_type,
                st.session_state.summary_length,
                st.session_state.model,
                st.session_state.selected_language
            )

        if st.session_state.summary:
            with st.spinner("The summary is being voiced..."):
                st.session_state.audio_path = voiceover(st.session_state.summary)
            st.success("Audio summary generated successfully!")

    # Always display summary and audio if they exist
    if st.session_state.summary:
        st.subheader("Video Summary")
        st.write(st.session_state.summary)
        if st.session_state.audio_path:
            st.audio(st.session_state.audio_path, format="audio/mp3")

    # Initialize Chroma Vectorstore (if video URL is provided)
    retriever = None
    if st.session_state.video_url:
        retriever = initialize_vectorstore(st.session_state.video_url)

    # Chat interface
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input for chat
    if prompt := st.chat_input("What is up?"):
        if retriever is not None:
            # Retrieve context from Chroma
            related_docs = retriever.get_relevant_documents(prompt)
            context = "\n\n".join([doc.page_content for doc in related_docs])
        else:
            context = ""

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_obj = get_chain().invoke(
                {"question":prompt, "context": context},
                config = {"configurables": {"thread_id": "abcd_123"}}
            )
            #response_text = response_obj.content
            st.markdown(response_obj)

        st.session_state.messages.append({"role": "assistant", "content": response_obj})
