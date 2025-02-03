import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai  import ChatGoogleGenerativeAI

def get_available_models():
    return {
        "OpenAI GPT-4o": os.getenv("OPENAI_API_KEY"),
        "Anthropic Claude": os.getenv("ANTHROPIC_API_KEY"),
        "Google Gemini": os.getenv("GOOGLE_API_KEY")
    }


def check_api_key(selected_model):
    available_models = get_available_models()
    env_var = available_models.get(selected_model)

    if env_var:
        return True
    return False

def choose_model(selected_model: str):

    if check_api_key(selected_model):
        if selected_model == "OpenAI GPT-4o":
            return ChatOpenAI(model="gpt-4o-mini")
        elif selected_model == "Anthropic Claude":
            return ChatAnthropic(model="claude-3-opus-latest")
        else:
            return ChatGoogleGenerativeAI("gemini-1.5-pro")

    return None