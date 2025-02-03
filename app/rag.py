from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI

from app.vectordb import vectordb

# Define prompt for question-answering
prompt = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
"""

prompt_template = PromptTemplate.from_template(prompt)



# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class RAG:
    def __init__(self):
        graph = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph.add_edge(START, "retrieve")
        self.graph = graph.compile()

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)

    def retrieve(self, state: State):
        retrieved_docs = vectordb.retrieve(state["question"])
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt_template.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}


vectordb.embed_docs('/home/hoang/Downloads/bioengineering-11-00365.pdf')
# rag = RAG()
# rs = rag.graph.invoke({"question": "The model structure of the proposed combination of WNet and BiLSTM"})
# print(rs)