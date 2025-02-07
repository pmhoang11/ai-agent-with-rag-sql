import os

from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END

from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

from app.core.config import settings
from app.query_relation_db import RelationDB
from app.rag import RAG
from loguru import logger


@tool
def get_rag(question: str, space_id: int):
    """
    This tool performs Retrieval-Augmented Generation (RAG) within the agent, \
enabling dynamic knowledge retrieval before generating responses. \
It queries a specified knowledge base (documents) and returns relevant context to improve accuracy and relevance in AI-generated outputs. \
Ideal for handling complex queries, knowledge-intensive tasks, and real-time updates.\
    """
    rag = RAG()
    result = rag.graph.invoke({"question": question, "space_id": space_id})
    return result["answer"]

@tool
def get_sql(question: str):
    """
    The SQL Query Tool enables users to retrieve structured data by converting natural language queries into SQL statements. \
It allows querying workspace and space metadata, such as last updated timestamps, document counts, and other relevant attributes, \
ensuring precise and efficient data access.\
    """
    rdb = RelationDB()
    result = rdb.graph.invoke({"question": question})

    return result["answer"]


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class Agent:
    def __init__(self, tools, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        # graph.add_node("action", tool_node)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            logger.info(f"Calling: {t}")
            if not t['name'] in self.tools:      # check for bad tool name from LLM
                logger.info("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        logger.info("Back to the model!")
        return {'messages': results}


prompt = """
You are an intelligent assistant with access to multiple tools to retrieve and process information efficiently. Your goal is to provide accurate, relevant, and concise responses based on the user's query. 

Available Tools:
get_rag – Retrieves relevant content from documents using a Retrieval-Augmented Generation (RAG) system. Use this tool when the user requests information from documents.
get_sql – Queries metadata about documents, such as workspace, space, update date, and other document-related attributes. Use this tool when metadata is required.

Decision-Making Guidelines:
You may answer directly without using tools if the information is already known or can be inferred logically.
Use get_rag when the user requires document content, summaries, or explanations based on stored knowledge.
Use get_sql when metadata about a document is explicitly requested.
Combine tools if necessary to provide a comprehensive response.
If the user’s request is unclear, ask clarifying questions before proceeding.


Step-by-Step Reasoning Process
1. Question: The user’s input question.
2. Thought: Analyze the intent of the question and determine what information is needed.
3. Action: Decide on the necessary action (whether to use a tool or answer directly).
4. Action Input: Provide input for the selected action.
5. Observation: Capture the result from the action taken.
6. (Repeat Thought/Action/Action Input/Observation if needed)
7. Thought: Determine if enough information has been gathered.
8. Final Answer: Provide the final response.

Example: Combined Tool Usage
    User Question: "Give me the summary of the latest updated document in workspace A."
    Thought: I need to find the latest updated document in workspace A. First, I will use get_sql to retrieve the document title.
    Action: Use get_sql.
    Observation: The latest updated document is "Document X".
    Thought: Now that I have the document title, I will use get_rag to retrieve its summary.
    Action: Use get_rag.
    Observation: The summary of Document X is "...(summary content)...".
    Thought: I now have the final answer.
    Final Answer: "The latest updated document in workspace A is Document X. Here is its summary: ...(summary content)..."
    
Example: Using get_rag to Summarize a Document
    User Question: "Summarize document Y."
    Thought: The user wants a summary of document Y. I need to retrieve its content using get_rag.
    Action: Use get_rag.
    Action Input: { "document": "Y", "type": "summary" }
    Observation: The summary of Document Y is "...(summary content)...".
    Thought: I now have the final answer.
    Final Answer: "...(summary content)..."
    
Example: Using get_sql to Find the Workspace of the Latest Uploaded Document
    User Question: "Find the workspace where User123 uploaded the latest document."
    Thought: I need to find the latest document uploaded by User123 and determine its workspace. Since workspaces contain spaces, I only need to retrieve the workspace directly from user_id.
    Action: Use get_sql.
    Observation: Latest document was uploaded in Workspace_A.
    Final Answer: "User123's latest document is in Workspace_A."
    
        
Response Guidelines:
Prioritize accuracy and relevance in responses.
If no relevant information is found, inform the user instead of making assumptions.
Be efficient—avoid unnecessary tool usage if the answer can be provided directly.

Your primary goal is to deliver precise, context-aware, and well-structured responses while optimizing tool usage.
"""

tools = [get_rag, get_sql]
# tool_node = ToolNode(tools)

agent = Agent(tools, system=prompt)
