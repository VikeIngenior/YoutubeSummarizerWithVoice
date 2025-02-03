import streamlit as st
import re
from summarize import summarize_transcript
from transcript import transcript_from_youtubeloader
from voiceover import voiceover
from choose_model import get_available_models, choose_model

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
    st.markdown(" Type the URL and get the Summary!")

    # User input for the URL
    video_url = st.text_input("Enter the URL:")

    # Sidebar settings
    with st.sidebar:
        st.markdown("### Summary Settings")
        summary_type = st.selectbox(
            "Choose the type of the summary:",
            ['First-Person', 'Third-Person'],
            index=1
        )

        summary_length = st.selectbox(
            "Choose the length of the summary:",
            ['Short', 'Long'],
            index=0
        )

        st.markdown("### Choose a Model")
        model_options = list(get_available_models().keys())
        selected_model = st.selectbox("Select a model for summarization:", model_options)

        LLM = choose_model(selected_model)

        # Model Information
        if LLM is not None:
            model_mapping = {
                "OpenAI GPT-4o": "GPT-4o Mini",
                "Anthropic Claude": "Claude 3 Opus",
                "Google Gemini": "Gemini 1.5 Pro"
            }

            selected_model_info = model_mapping.get(selected_model, "Unknown Model")
            st.info(f"Using **{selected_model_info}** for summarization.")
        else:
            st.warning("No API Key was found for the chosen model!")

        st.markdown("### Choose the Summary Language.")
        language_options = ["Original Language", "English", "Turkish","Spanish", "French", "German"]
        selected_language = st.selectbox("Select the output language:", language_options, index=0)

    # Summarization button logic
    if st.button("Summarize"):
        if not video_url or (video_url and not is_valid_youtube_url(video_url)):
            st.warning("Please enter a valid URL!")
            return

        with st.spinner("Getting the transcript..."):
            docs = transcript_from_youtubeloader(video_url)

        if not docs:
            st.error("Transcript could not be obtained.")
            return

        with st.spinner("Transcript is being summarized..."):
            summary = summarize_transcript(docs, summary_type, summary_length, LLM, selected_language)

        if summary:
            st.subheader("Video Summary")
            st.write(summary)

            with st.spinner("The summary is being voiced..."):
                audio_path = voiceover(summary)

            st.success("Audio summary generated successfully!")
            st.audio(audio_path, format="audio/mp3")