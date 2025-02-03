import os
from typing_extensions import Annotated, TypedDict
from loguru import logger

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from langchain_chroma import Chroma
from app.core.config import settings
from uuid import uuid4

from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_docs(file_path) -> list[Document]:
    loader = PyPDFLoader(file_path)

    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=20,
        length_function=len,
        separators=["\n\n", "\n", " "],
    )
    docs = text_splitter.split_documents(raw_documents)

    return docs

class VectorDB:
    def __init__(self):
        self.client = chromadb.Client()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            client=self.client,
            collection_name="test_abc_123",
            embedding_function=self.embeddings,
        )

    def embed_docs(self, file_path):
        try:
            docs = load_docs(file_path)
            uuids = [str(uuid4()) for _ in range(len(docs))]

            self.vector_store.add_documents(documents=docs, ids=uuids)
        except Exception as e:
            logger.error(e)

    def retrieve(self, question: str, score_thr=1.8, k=5):
        try:
            retrieved_docs = self.vector_store.similarity_search_with_score(question, k=k)
            docs = []
            for doc, score in retrieved_docs:
                if score <= score_thr:
                    docs.append(doc)
            return docs
        except Exception as e:
            logger.error(e)


vectordb = VectorDB()
