import re
from langchain.chains.combine_documents import create_stuff_documents_chain
from constants import FIRST_PERSON_PROMPT, THIRD_PERSON_PROMPT
import streamlit as st
from typing import Optional, List

def summarize_transcript(docs: List, prompt_type:  str, length: str, llm, language: str) -> Optional[str]:
    """
    Summarizes the transcript using an LLM model.

    Args:
        docs (List): The transcript documents to be summarized.
        prompt_type (str): Type of summary ('First-Person' or 'Third-Person').
        length (str): Length of summary ('Short' or 'Long').
        llm: The language model instance used for summarization.
        language (str): Output language of the summary.

    Returns:
        Optional[str]: The summarized text if successful, otherwise None.
    """
    summary_type = {"First-Person": FIRST_PERSON_PROMPT, "Third-Person": THIRD_PERSON_PROMPT}
    summary_length = {"Short": 2, "Long": 7}

    if llm is not None: # If there is an API key for the selected model.
        try:
            chain = create_stuff_documents_chain(llm, summary_type.get(prompt_type))
            result = chain.invoke({"context": docs, "length": summary_length.get(length), "language": language})
            return result
        except Exception as e:
            match = re.search(r"'message': '([^']*)'", str(e))
            error_message = match.group(1) if match else "Unknown Error! (Probably the balance is too low for the API Key.)"
            st.error(error_message)
            return None