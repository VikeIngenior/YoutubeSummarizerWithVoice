import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai  import ChatGoogleGenerativeAI
from typing import Union
from langchain_deepseek import ChatDeepSeek

def get_available_models():
    return {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic Claude": os.getenv("ANTHROPIC_API_KEY"),
        "Google Gemini": os.getenv("GOOGLE_API_KEY"),
        "DeepSeek": os.getenv("DEEPSEEK_API_KEY"),
    }


def check_api_key(selected_model: str) -> bool:
    """
    Check if an API key (env variable) exists for the selected model.

    Args:
        selected_model (str): The selected model to check.
    Returns:
        bool: True if the API key exists, False otherwise.
    """

    available_models = get_available_models()
    env_var = available_models.get(selected_model)

    if env_var:
        return True
    return False

def choose_model(selected_model: str) -> Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatDeepSeek, None]:
    """
    Selects and returns a chatbot model based on the given model name.

    This function checks if an API key is available for the selected model.
    If available, it returns the corresponding chatbot model instance.
    If no API key is found, it returns None.

    Args:
        selected_model (str): The name of the AI model to use.
    Returns:
        Model or None: An instance of the selected chatbot model, or None if
        the API key is not available.
    """
    if check_api_key(selected_model):
        if selected_model == "OpenAI":
            return ChatOpenAI(model="gpt-4o-mini")
        elif selected_model == "Anthropic Claude":
            return ChatAnthropic(model="claude-3-opus-latest")
        elif selected_model == "Google Gemini":
            return ChatGoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp-01-21")
        elif selected_model == "DeepSeek":
            return ChatDeepSeek(model="deepseek-chat")

    return None