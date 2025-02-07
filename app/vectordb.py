import os
from typing_extensions import Annotated, TypedDict
from loguru import logger

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
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
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            collection_name="test_abc_123",
            embedding_function=self.embeddings,
            persist_directory=settings.VECTORDB_PERSIST_DIR
        )


    def embed_docs(self, file_path, space_id:int, document_id:int):
        try:
            docs = load_docs(file_path)
            uuids = [str(uuid4()) for _ in range(len(docs))]
            for doc in docs:
                doc.metadata["space_id"] = space_id
                doc.metadata["document_id"] = document_id
            self.vector_store.add_documents(documents=docs, ids=uuids)
            return uuids
        except Exception as e:
            logger.error(e)

    def retrieve(self, question: str, score_thr=2, k=15, space_id=None):
        try:
            if space_id:
                retrieved_docs = self.vector_store.similarity_search_with_score(
                    question,
                    k=k,
                    filter={"space_id": space_id}
                )
            else:
                retrieved_docs = self.vector_store.similarity_search_with_score(
                    question,
                    k=k
                )

            docs = []
            for doc, score in retrieved_docs:
                if score <= score_thr:
                    docs.append(doc)
            return docs
        except Exception as e:
            logger.error(e)


vectordb = VectorDB()
