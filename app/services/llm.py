from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings


def get_llm(model_name: str = None, temperature: float = 0.2):
    """Instantiate and return the configured Gemini Chat model."""
    settings = get_settings()
    model = model_name or settings.MODEL_NAME
    api_key = settings.GEMINI_API_KEY

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please provide it in your environment or .env file."
        )

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature
    )
