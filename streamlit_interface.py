import streamlit as st
import re
import os
from ingestion import initialize_vectorstore, get_chain
from choose_model import get_available_models, choose_model
from oop_based_youtube_video import Video

def is_valid_youtube_url(url):
    """
    Checks if the provided URL is a valid YouTube link.
    """
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
    return youtube_pattern.match(url)

def streamlit_oop_last():
    """
    Streamlit interface for summarizer.

    Steps:
      - Create a Video object (if URL has changed or not yet created)
      - Retrieve the transcript from the video
      - Generate a summary using the provided transcript, model and settings
      - Generate audio for the summary (if an OpenAI API key is provided)
      - Initialize a retriever using the transcripts of the video
      - Display the summary and audio
      - Provide a chat interface for Q&A using the summary and retriever context

    Session state is used to keep data between reruns.
    """

    # Initialize session state keys
    if "video_url" not in st.session_state:
        st.session_state.video_url = ""
    if "current_url" not in st.session_state:
        st.session_state.current_url = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "video_obj" not in st.session_state:
        st.session_state.video_obj = None
    if "retriever" not in st.session_state:
        st.session_state.retriever = None

    # Page header
    st.title("Youtube Video Summarizer")
    st.markdown("Type the URL and get the Summary!")

    # Sidebar settings
    with st.sidebar:
        st.markdown("### Summary Settings")
        # Select summary type and length
        summary_type = st.selectbox("Choose summary type:", ["Third-Person", "First-Person"])
        summary_length = st.selectbox("Choose summary length:", ["Short", "Long"])

        st.markdown("### Choose a Model")
        model_options = list(get_available_models().keys())
        selected_model = st.selectbox("Select a model for summarization:", model_options)

        # Get the APIs for selected models
        if selected_model == "OpenAI":
            default_api = os.getenv("OPENAI_API_KEY", "")
            openai_api = st.text_input("Enter OpenAI API Key:", value=default_api, type="password")
            os.environ["OPENAI_API_KEY"] = openai_api
        elif selected_model == "Anthropic Claude":
            default_api = os.getenv("ANTHROPIC_API_KEY", "")
            anthropic_api = st.text_input("Enter Anthropic API Key:", value=default_api, type="password")
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api
        elif selected_model == "Google Gemini":
            default_api = os.getenv("GOOGLE_API_KEY", "")
            google_api = st.text_input("Enter Google API Key:", value=default_api, type="password")
            os.environ["GOOGLE_API_KEY"] = google_api
        elif selected_model == "DeepSeek":
            default_api = os.getenv("DEEPSEEK_API_KEY", "")
            deepseek_api = st.text_input("Enter DeepSeek API Key:", value=default_api, type="password")
            os.environ["DEEPSEEK_API_KEY"] = deepseek_api

        # Create the model instance from the selected model
        model_instance = choose_model(selected_model)
        if model_instance is not None:
            model_mapping = {
                "OpenAI": "GPT-4o Mini",
                "Anthropic Claude": "Claude 3 Opus",
                "Google Gemini": "Gemini 2.0 Flash",
                "DeepSeek": "DeepSeek-V3",
            }
            selected_model_info = model_mapping.get(selected_model, "Unknown Model")
            st.info(f"Using **{selected_model_info}** for summarization.")
        else:
            st.warning("No API Key was found for the chosen model!") # Only way for the model to be None is if there is no API key provided

        st.markdown("### Choose the Summary Language")
        language = st.selectbox("Select the output language:",
                                ["Original Language", "English", "Turkish", "Spanish", "French", "German"])

    if model_instance is None:
        st.info("Please choose a model and enter the API key.")
        st.info("Note: You must enter an OpenAI API key if you want to get an audio of the summary!")

    # Create the video object only if it doesn't exist or if the URL has changed.
    st.session_state.video_url = st.text_input("Enter the URL:", value=st.session_state.video_url)
    if not st.session_state.video_obj or st.session_state.video_url != st.session_state.current_url:
        st.session_state.video_obj = Video(st.session_state.video_url)

    if model_instance is not None:
        if st.button("Summarize"):
            # Check if the URL is valid
            if not is_valid_youtube_url(st.session_state.video_url):
                st.warning("Please enter a valid URL!")
                return

            # Clear old data if a new URL is provided
            if st.session_state.video_url != st.session_state.current_url:
                st.session_state.video_obj = None
                st.session_state.messages = []
                st.session_state.retriever = None
                st.session_state.current_url = st.session_state.video_url

            if st.session_state.video_obj is None:
                st.session_state.video_obj = Video(st.session_state.video_url)

            # Get transcript from the video.
            with st.spinner("Getting the transcript..."):
                st.session_state.video_obj.get_transcript()
                if st.session_state.video_obj.transcript is None:
                    st.error("Transcript could not be obtained.")
                    st.stop()

            # Summarize transcript
            with st.spinner("Summarizing transcript..."):
                st.session_state.video_obj.get_summary(model_instance, summary_type, summary_length, language)

            if st.session_state.video_obj.summary:
                # Don't generate audio if no OPENAI API key is provided
                if not os.getenv("OPENAI_API_KEY"):
                    st.warning("No OpenAI API key provided; audio summary generation is disabled.")
                    st.session_state.video_obj.audio = None
                else:
                    with st.spinner("Generating audio summary..."):
                        try:
                            st.session_state.video_obj.voiceover(os.getenv("OPENAI_API_KEY"))
                        except Exception as e:
                            st.error("Error generating audio: " + str(e))

            # Initialize the retriever
            if st.session_state.retriever is None:
                try:
                    st.session_state.retriever = initialize_vectorstore(st.session_state.video_url)
                except Exception as e:
                    st.error("Error initializing vectorstore: " + str(e))

        # Display the generated summary and audio if available.
        if st.session_state.video_obj is not None and st.session_state.video_obj.summary:
            st.subheader("Video Summary")
            st.write(st.session_state.video_obj.summary)
            if st.session_state.video_obj.audio:
                st.audio(st.session_state.video_obj.audio, format="audio/mp3")

            # Display chat messages from history.
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Accept user input for chat.
            if prompt := st.chat_input("Ask your question:"):
                # Retrieve context from vectorstore if available
                try:
                    if st.session_state.retriever is not None:
                        related_docs = st.session_state.retriever.get_relevant_documents(prompt)
                        context = "\n\n".join([doc.page_content for doc in related_docs])
                    else:
                        context = ""
                except Exception as e:
                    st.error("Error retrieving context: " + str(e))
                    context = ""
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                try:
                    # Append conversation history to the prompt
                    with st.chat_message("assistant"):
                        history_str = "\n".join(
                            [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
                        response_obj = get_chain(model_instance).invoke(
                            {"question": prompt, "context": context, "history": history_str}
                        )
                        response_text = response_obj if isinstance(response_obj, str) else response_obj.content
                        st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error("Error in chat response: " + str(e))