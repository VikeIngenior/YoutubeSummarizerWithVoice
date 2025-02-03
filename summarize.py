import re
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from constants import FIRST_PERSON_PROMPT, THIRD_PERSON_PROMPT
import streamlit as st
from typing import List
load_dotenv()

def summarize_transcript(docs: List, prompt_type:  str, length: str, LLM):

    type_and_length = [{"First-Person": FIRST_PERSON_PROMPT, "Third-Person": THIRD_PERSON_PROMPT},
                       {"Short": 2, "Long": 7}]
    print("LLM TYPE IN SUMMARIZER: ",LLM)
    if LLM is not None:
        try:
            chain = create_stuff_documents_chain(LLM, type_and_length[0][prompt_type])
            #print(f"______________\n{type_and_length[0][prompt_type]}\n__________________________")
            result = chain.invoke({"context": docs, "length": type_and_length[1].get(length)})
            #print(llm.usage_metadata)
            #print(result)
            return result
        except Exception as e:
            match = re.search(r"'message': '([^']*)'", str(e))  # 'message' içindeki değeri al
            error_message = match.group(1) if match else "Unknown Error! (Probably the balance is too low for the API Key."

            st.error(error_message)
