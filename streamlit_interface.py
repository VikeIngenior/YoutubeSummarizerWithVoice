import streamlit as st
import re
from summarize import summarize_transcript
from transcript import transcript_from_youtubeloader
from voiceover import voiceover
from choose_model import get_available_models, choose_model
import constants

docs = []

def is_valid_youtube_url(url):
    # YouTube URL'sinin geçerliliğini kontrol etmek için regex kullanılır
    youtube_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')
    return youtube_pattern.match(url)

def streamlit_interface():
    st.title("Youtube Summarizer")
    st.markdown("""
        Type the URL and get the Summary!
    """)

    video_url = st.text_input("Enter the URL:")

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
        constants.LLM = choose_model(selected_model)

    if st.button("Summarize"):
        if not video_url or (video_url and not is_valid_youtube_url(video_url)):
            st.warning("Please enter a valid URL!")
        else:
            with st.spinner("Getting the transcript..."):
                docs = transcript_from_youtubeloader(video_url)
            if docs:
                with st.spinner("Transcript is being summarized..."):
                    summary = summarize_transcript(docs, summary_type, summary_length)
                if summary:
                    st.subheader("Video Summary")
                    st.write(summary)

                    audio_path = voiceover(summary)
                    st.success("The summary is being voiced...")

                    st.audio(audio_path, format='audio/mp3')
            else:
                st.error("Transcript could not be obtained.")
