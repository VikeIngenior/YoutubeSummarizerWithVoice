from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from constants import FIRST_PERSON_PROMPT, THIRD_PERSON_PROMPT, LLM
from typing import List
load_dotenv()


def summarize_transcript(docs: List, prompt_type:  str, length: str):

    type_and_length = [{"First-Person": FIRST_PERSON_PROMPT, "Third-Person": THIRD_PERSON_PROMPT},
                       {"Short": 2, "Long": 7}]

    chain = create_stuff_documents_chain(LLM, type_and_length[0][prompt_type])
    #print(f"______________\n{type_and_length[0][prompt_type]}\n__________________________")
    result = chain.invoke({"context": docs, "length": type_and_length[1].get(length)})
    #print(llm.usage_metadata)
    #print(result)
    return result
