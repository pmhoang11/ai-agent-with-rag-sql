import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PERSIST_DIR = "/home/hoangphan/Data/vectordb"

COLLECTION_NAME = "test_abc_123"
# COLLECTION_NAME = "test_basic"