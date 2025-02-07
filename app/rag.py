from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI

from app.rerank import rerank_results
from app.vectordb import vectordb

from loguru import logger

# Define prompt for question-answering
prompt = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
Question: {question} 
Context: {context} 
"""

prompt_template = PromptTemplate.from_template(prompt)



# Define state for application
class State(TypedDict):
    question: str
    space_id: int
    context: List[Document]
    answer: str


class RAG:
    def __init__(self):
        graph = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph.add_edge(START, "retrieve")
        self.graph = graph.compile()

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)

    def retrieve(self, state: State):
        logger.info("Start Retrieve")
        retrieved_docs = vectordb.retrieve(state["question"], space_id=state["space_id"])
        if len(retrieved_docs) == 0:
            return {"context": retrieved_docs}
        logger.info("Start Rerank")
        reranked_results = rerank_results(state["question"], retrieved_docs)
        return {"context": reranked_results}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt_template.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}
