import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings(BaseSettings):
    DATABASE_URL = os.getenv("DB_CONNECTION_STRING", "")

    # OPENAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MAX_LENGTH_TOKEN = int(os.getenv("OPENAI_MAX_LENGTH_TOKEN", 4096))
    OPENAI_MODEL = "gpt-4o-mini"

    RETRY_TIMEOUT = int(os.getenv("RETRY_TIMEOUT", 15000))

    # LANGSMITH
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", False)
settings = Settings()
