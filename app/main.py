from app.db.user import UsersService
from app.models.base import Base
from app.db.base import engine

from sqlalchemy import create_engine, inspect
from app.schemas.user_request import UserRequest
import os
from typing_extensions import Annotated
from typing_extensions import TypedDict

# Base.metadata.create_all(bind=engine)
# # inspector = inspect(engine)
#
# us = UsersService()
# # new_user = UserRequest(username='ABC')
# # us.add_user(new_user, super_user_id=999)
# uss = us.get_all_users()
# pass

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
from app.core.config import settings


db = SQLDatabase.from_uri("postgresql://postgres:V8NPK74XBhuLMIHWTnJfbZBN@0.0.0.0:5432/data-db")
print(db.dialect)
print(db.get_usable_table_names())
# db.run("SELECT * FROM Artist LIMIT 10;")

query_prompt = """
Given an input question, create a syntactically correct {dialect} query to run to help find the answer. Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Only use the following tables:
{table_info}

Question: {input}"""

query_prompt_template = PromptTemplate.from_template(query_prompt)


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    print(result)
    return {"query": result["query"]}

def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

# write_query({"question": "How many Employees are there?"})
# rs = execute_query({"query": "SELECT COUNT(*) AS employee_count FROM users;"})


graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()
for step in graph.stream(
    {"question": "How many employees are there?"}, stream_mode="updates"
):
    print(step)

# chain = create_sql_query_chain(llm, db)
# response = chain.invoke({"question": "How many employees are there"})
