import json
import os
from typing import List
from uuid import uuid4

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

import config
from langchain_chroma import Chroma
from loguru import logger
from multiprocessing.pool import Pool

DOCUMENT_CONTEXT_PROMPT = """
<document>
{doc_content}
</document>
"""

CHUNK_CONTEXT_PROMPT = """
Here is the chunk we want to situate within the whole document
<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
Answer directly with the content of the chunk without prefacing it with phrases like 'The chunk provides...' or 'This chunk is part of...'. Focus solely on delivering the relevant information.
"""

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=1024
)

def load_docs(file_path) -> (str, List[Document]):
    loader = PyPDFLoader(file_path)

    raw_documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=20,
        length_function=len,
        separators=["\n\n", "\n", " "],
    )
    docs = text_splitter.split_documents(raw_documents)
    contextual = list(map(lambda x: x.page_content, docs))
    window_size = 3
    n = len(contextual)
    contextual = [" ".join(contextual[max(0, i - window_size // 2): min(n, i - window_size // 2 + window_size)]) for i in range(n)]

    return contextual, docs



def process_work_contextual(args):
    doc, chunk = args
    mess = [
        HumanMessage(content=DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc["content"])),
        HumanMessage(content=CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk["content"])),
    ]
    response = llm.invoke(mess)

    contextualized_text = response.content

    result = {
        'text_to_embed': f"{chunk['content']}\n\n{contextualized_text}",
        'metadata': {
            'doc_id': doc['doc_id'],
            'original_uuid': doc['original_uuid'],
            'chunk_id': chunk['chunk_id'],
            'original_index': chunk['original_index'],
            'original_content': chunk['content'],
            'contextualized_content': contextualized_text
        }
    }

    return result

def process_work_basic(args):
    doc, chunk = args

    result = {
        'text_to_embed': chunk['content'],
        'metadata': {
            'doc_id': doc['doc_id'],
            'original_uuid': doc['original_uuid'],
            'chunk_id': chunk['chunk_id'],
            'original_index': chunk['original_index'],
            'original_content': chunk['content'],
        }
    }

    return result

class ContextualVectorDB:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=config.PERSIST_DIR
        )

    def embed_docs_contextual(self, file_path):
        try:
            with open(file_path, 'r') as f:
                dataset = json.load(f)

            texts_to_embed = []
            metadata = []
            args = []
            for doc in dataset:
                for chunk in doc['chunks']:
                    args.append((doc, chunk))

            with Pool(processes=os.cpu_count() - 3) as pool:
                with tqdm(total=len(args), desc="Processing Docs") as pbar:
                    for result in pool.imap_unordered(process_work_contextual, args):
                        texts_to_embed.append(result["text_to_embed"])
                        metadata.append(result["metadata"])
                        pbar.update(1)

            uuids = [str(uuid4()) for _ in range(len(texts_to_embed))]

            self.vector_store.add_texts(texts=texts_to_embed, metadatas=metadata)
            return uuids
        except Exception as e:
            logger.error(e)

    def embed_docs_basic(self, file_path):
        try:
            with open(file_path, 'r') as f:
                dataset = json.load(f)

            texts_to_embed = []
            metadata = []
            args = []
            for doc in dataset:
                for chunk in doc['chunks']:
                    args.append((doc, chunk))

            with Pool(processes=os.cpu_count() - 3) as pool:
                with tqdm(total=len(args), desc="Processing Docs") as pbar:
                    for result in pool.imap_unordered(process_work_basic, args):
                        texts_to_embed.append(result["text_to_embed"])
                        metadata.append(result["metadata"])
                        pbar.update(1)

            uuids = [str(uuid4()) for _ in range(len(texts_to_embed))]

            self.vector_store.add_texts(texts=texts_to_embed, metadatas=metadata)
            return uuids
        except Exception as e:
            logger.error(e)

    def retrieve(self, question: str, score_thr=2, k=15):
        try:

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

context_vectordb = ContextualVectorDB()
