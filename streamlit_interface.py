import streamlit as st
import re
import os
from ingestion import initialize_vectorstore, get_chain
from summarize import summarize_transcript
from transcript import transcript_from_youtubeloader
from voiceover import voiceover
from choose_model import get_available_models, choose_model
from dotenv import load_dotenv
load_dotenv()

docs = []

def is_valid_youtube_url(url):
    """
    Checks if the provided URL is a valid YouTube link.
    """
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
    return youtube_pattern.match(url)

def streamlit_interface():
    st.title("Youtube Video Summarizer")
    st.markdown("Type the URL and get the Summary!")
    st.info("Note: You must enter an OpenAI API key if you want to get an audio of the summary!")

    # Initialize session state keys (if not already set)
    if "video_url" not in st.session_state:
        st.session_state.video_url = ""
    if "current_url" not in st.session_state:
        st.session_state.current_url = ""
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

    # Transcript, summary, audio and retriever storage
    if "docs" not in st.session_state:
        st.session_state.docs = None
    if "summary" not in st.session_state:
        st.session_state.summary = ""
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = ""
    if "retriever" not in st.session_state:
        st.session_state.retriever = None

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

        print(st.session_state.selected_model)

        # Yeni: Seçilen modele göre API Key girme alanı.
        if st.session_state.selected_model == "OpenAI GPT-4o":
            default_api = os.getenv("OPENAI_API_KEY", "")
            st.session_state.openai_api_key = st.text_input("Enter OpenAI API Key:", value=default_api, type="password")
            os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
        elif st.session_state.selected_model == "Anthropic Claude":
            default_api = os.getenv("ANTHROPIC_API_KEY", "")
            st.session_state.anthropic_api_key = st.text_input("Enter Anthropic API Key:", value=default_api, type="password")
            os.environ["ANTHROPIC_API_KEY"] = st.session_state.anthropic_api_key
        elif st.session_state.selected_model == "Google Gemini":
            default_api = os.getenv("GOOGLE_API_KEY", "")
            st.session_state.google_api_key = st.text_input("Enter Google API Key:", value=default_api, type="password")
            os.environ["GOOGLE_API_KEY"] = st.session_state.google_api_key

        # Show information to the user about the model.
        st.session_state.model = choose_model(st.session_state.selected_model)
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

    if st.session_state.model is not None:
        # If the user clicks the "Summarize" button with a new URL, old data will be renewed.
        if st.button("Summarize"):
            if not st.session_state.video_url or not is_valid_youtube_url(st.session_state.video_url):
                st.warning("Please enter a valid URL!")
                return

            # If the given URL is different from the previous URL, clean the old data.
            if st.session_state.video_url != st.session_state.current_url:
                st.session_state.docs = None
                st.session_state.summary = ""
                st.session_state.audio_path = ""
                st.session_state.retriever = None
                st.session_state.messages = []
                st.session_state.current_url = st.session_state.video_url

            with st.spinner("Getting the transcript..."):
                # Create transcript only once per URL
                if st.session_state.docs is None:
                    docs = transcript_from_youtubeloader(st.session_state.video_url)
                    st.session_state.docs = docs
                else:
                    docs = st.session_state.docs

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
                # Check if an OPENAI_API_KEY provided to create an audio
                if not st.session_state.openai_api_key:
                    st.warning("No OpenAI API key provided; audio summary generation is disabled.")
                    st.session_state.audio_path = ""
                else:
                    with st.spinner("The summary is being voiced..."):
                        st.session_state.audio_path = voiceover(st.session_state.summary)
                    st.success("Audio summary generated successfully!")

            # Create the vectorstore and retriever only once per URL
            if st.session_state.retriever is None:
                st.session_state.retriever = initialize_vectorstore(st.session_state.video_url)

        # Display the summary and audio every time the interface reruns.
        if st.session_state.summary:
            st.subheader("Video Summary")
            st.write(st.session_state.summary)
            if st.session_state.audio_path:
                st.audio(st.session_state.audio_path, format="audio/mp3")

            # Chat interface (shown only after summarization)
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Accept user input for chat.
            if prompt := st.chat_input("What is up?"):
                # Get related docs if available.
                if st.session_state.retriever is not None:
                    related_docs = st.session_state.retriever.get_relevant_documents(prompt)
                    context = "\n\n".join([doc.page_content for doc in related_docs])
                else:
                    context = ""

                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                try:
                    with st.chat_message("assistant"):
                        response_obj = get_chain(st.session_state.model).invoke(
                            {"question": prompt, "context": context},
                            config={"configurables": {"thread_id": "abcd_123"}}
                        )
                        response_text = response_obj if isinstance(response_obj, str) else response_obj.content
                        st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    match = re.search(r"'message': '([^']*)'", str(e))
                    error_message = match.group(1) if match else ("Unknown Error! (Probably no API for the chosen model or the balance is too low for the API Key.)")
                    st.error(error_message)
    else:
        st.error("Please choose a model with an API key.")
