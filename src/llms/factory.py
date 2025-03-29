
import os
import logging
from functools import lru_cache
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# Cache API keys to avoid repeated lookups
API_KEYS = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY"),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
}

# Set environment variables
# for key, value in API_KEYS.items():
#     if value:
#         os.environ[key] = value


@lru_cache(maxsize=16)
def get_llm(model_type, model_name=None):
    try:
        if model_type == "groq":
            return ChatGroq(model=model_name or "deepseek-r1-distill-qwen-32b")
        elif model_type == "google":
            return ChatGoogleGenerativeAI(model=model_name or "gemini-2.0-flash", temperature=0)
        elif model_type == "openai":
            return ChatOpenAI(model_name=model_name or "gpt-4")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    except Exception as e:
        logger.error(f"Error initializing LLM {model_type}/{model_name}: {e}")
        return ChatGroq(model="deepseek-r1-distill-qwen-32b")
