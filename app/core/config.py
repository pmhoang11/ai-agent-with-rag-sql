import os
import time
from loguru import logger
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

os.makedirs("/logs", exist_ok=True)
logger.add("/logs/app.log", retention="7 days", level="DEBUG")


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

    # DIR
    PDF_DIR = os.getenv("PDF_DIR", "/mnt/data/pdf")
    os.makedirs(PDF_DIR, exist_ok=True)

    # VECTORDB
    VECTORDB_PERSIST_DIR=os.getenv("VECTORDB_PERSIST_DIR", "")
    os.makedirs(VECTORDB_PERSIST_DIR, exist_ok=True)
    COLLECTION_NAME=os.getenv("COLLECTION_NAME", "")
    COLLECTION_METADATA={
        "hnsw:space": "cosine",
        "hnsw:num_threads": max(1, os.cpu_count() - 3),
        "hnsw:construction_ef": 100,  # Number of neighbors explored when adding new vectors
        "hnsw:M": 16,  # Maximum number of connections per vector
        "hnsw:search_ef": 10,  # Number of neighbors explored during search
    }


    @staticmethod
    def timeit(func):
        def wrapped(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
            return result

        return wrapped

settings = Settings()
