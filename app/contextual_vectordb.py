import os
from typing import List
from uuid import uuid4
from venv import logger

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

from app.core.config import settings
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



# def process_work(doc, context, space_id):
def process_work(args):
    doc, context, space_id, document_id = args
    mess = [
        HumanMessage(content=DOCUMENT_CONTEXT_PROMPT.format(doc_content=context)),
        HumanMessage(content=CHUNK_CONTEXT_PROMPT.format(chunk_content=doc.page_content)),
    ]
    response = llm.invoke(mess)

    doc.metadata["space_id"] = space_id
    doc.metadata["document_id"] = document_id
    doc.metadata["origin_content"] = doc.page_content
    doc.metadata["contextualized_content"] = response.content
    doc.page_content = f"{doc.page_content}\n\n{response.content}"
    return doc

class ContextualVectorDB:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.VECTORDB_PERSIST_DIR,
            collection_metadata=settings.COLLECTION_METADATA
        )

    @settings.timeit
    def embed_docs(self, file_path, space_id: int, document_id:int):
        try:
            contextual, docs = load_docs(file_path)
            args = [(doc, contextual[i], space_id, document_id) for i, doc in enumerate(docs)]

            with Pool(processes=max(1, os.cpu_count() - 3)) as pool:
                update_docs = []
                with tqdm(total=len(args), desc="Processing Docs") as pbar:
                    for result in pool.imap_unordered(process_work, args):
                        update_docs.append(result)
                        pbar.update(1)


            uuids = [str(uuid4()) for _ in range(len(update_docs))]

            self.vector_store.add_documents(documents=update_docs, ids=uuids)
            return uuids
        except Exception as e:
            logger.error(e)


context_vectordb = ContextualVectorDB()
