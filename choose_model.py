import os
from langchain_openai import ChatOpenAI

def get_available_models():
    return {
        "OpenAI GPT-4o": os.getenv("OPENAI_API_KEY"),
        "Anthropic Claude": os.getenv("ANTHROPIC_API_KEY"),
        "Google Gemini": os.getenv("GOOGLE_API_KEY")
    }


def check_api_key(selected_model):
    available_models = get_available_models()
    env_var = available_models.get(selected_model)

    if env_var and os.getenv(env_var):
        return True
    return False

def choose_model(selected_model: str):
    if check_api_key(selected_model):
        print("########################## bu model için api var")
