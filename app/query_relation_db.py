import os
from typing_extensions import Annotated, TypedDict


from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, END, StateGraph
from app.core.config import settings


db = SQLDatabase.from_uri("postgresql://postgres:V8NPK74XBhuLMIHWTnJfbZBN@0.0.0.0:5432/data-db")
print(db.dialect)
print(db.get_usable_table_names())

query_prompt = """
Given an input question, create a syntactically correct {dialect} query to run to help find the answer. Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
If the question does not seem related to the database, just return "I don't know" as the answer.

Only use the following tables:
{table_info}

Question: {input}"""

query_prompt_template = PromptTemplate.from_template(query_prompt)



class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]


class RelationDB:
    def __init__(self):
        # graph = StateGraph(State).add_sequence(
        #     [self.write_query, self.execute_query, self.generate_answer]
        # )
        graph = StateGraph(State)
        graph.add_node("write_query", self.write_query)
        graph.add_node("execute_query", self.execute_query)
        graph.add_node("generate_answer", self.generate_answer)


        graph.add_conditional_edges(
            "write_query",
            self.exists_action,
            {END: END, "execute_query": "execute_query"}
        )

        # graph.add_edge("write_query", "execute_query")
        graph.add_edge("execute_query", "generate_answer")
        graph.add_edge(START, "write_query")
        graph.add_edge("generate_answer", END)

        self.graph = graph.compile()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # self.tools = {t.name: t for t in tools}
        # self.model = model.bind_tools(tools)

    def exists_action(self, state: State):
        result = state["query"]
        print(result)
        compare =  "I don't know" == result
        if compare:
            return END
        else:
            return "execute_query"

    def write_query(self, state: State):
        """Generate SQL query to fetch information."""
        prompt = query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": state["question"],
            }
        )
        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        print(result)
        return {"query": result["query"]}

    def execute_query(self, state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDatabaseTool(db=db)
        return {"result": execute_query_tool.invoke(state["query"])}

    def generate_answer(self, state: State):
        """Answer question using retrieved information as context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            """If the question does not seem related to the database, just return "I don't know" as the answer."""
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["query"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = self.llm.invoke(prompt)
        return {"answer": response.content}


# model = ChatOpenAI(model="gpt-4o-mini")
# rdb = RelationDB()

# rdb.graph.get_graph().draw_png('test.png')

# rs = rdb.graph.invoke(
#     {"question": "How many employees are there?"}
# )
# print(rs)
# for step in rdb.graph.stream(
#     {"question": "How many users are there?"}, stream_mode="updates"
# ):
#     print(step)

# chain = create_sql_query_chain(llm, db)
# response = chain.invoke({"question": "How many employees are there"})
