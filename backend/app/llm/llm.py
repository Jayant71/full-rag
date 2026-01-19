from pyexpat import model
from langchain_openai import ChatOpenAI
from app.core.config import settings
from pydantic import SecretStr


def get_chat_model(temperature: float = 0.7) -> ChatOpenAI:
    model_name = settings.OPENAI_MODEL_NAME
    URL = settings.OPENAI_BASE_URL
    if URL:
        chat_model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(settings.OPENAI_API_KEY),  # type: ignore
            base_url=URL
        )
    else:
        chat_model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(settings.OPENAI_API_KEY),  # type: ignore
        )
    return chat_model


if __name__ == "__main__":
    model = get_chat_model()
    print(model)
