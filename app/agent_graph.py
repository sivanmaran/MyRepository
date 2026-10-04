from typing import TypedDict
from vector_retriever import retrieve_metadata
import ollama
from sql_guardrial import validate_sql
import duckdb
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict, total=False):

    # User input
    question: str

    # RAG / metadata
    metadata: dict
    schema: str

    # SQL generation
    sql: str

    # SQL validation
    validation_result: bool
    validation_message: str

    # SQL execution
    execution_result: str
    error: str

    # Self-healing
    repair_attempts: int

    # Final response
    answer: str

    # Token tracking
    llm_calls: int
    input_tokens: int
    output_tokens: int
    total_tokens: int


def retrieve_metadata_node(state: AgentState):

    question = state["question"]

    print("\n[Node] Retrieve Metadata")
    print("Question:", question)

    metadata = retrieve_metadata(question)

    print("\nRetrieved tables:")

    for table in metadata["tables"]:
        print("-", table["table"])

    return {
        "metadata": metadata
    }


def generate_sql_node(state: AgentState):

    question = state["question"]
    metadata = state["metadata"]

    print("\n[Node] Generate SQL")

    # Build schema dynamically from retrieved metadata
    schema = ""

    for table in metadata["tables"]:

        schema += f"\n{table['table']}:\n"

        for column, description in table["columns"].items():
            schema += f"- {column}: {description}\n"

    print("\nDynamic Schema:")
    print(schema)

    prompt = f"""
You are a SQL generation assistant.

Generate a DuckDB SQL query for the user's question.

Use ONLY the tables and columns provided below.

Schema:
{schema}

User question:
{question}

Rules:
- Generate only SQL.
- Do not explain the SQL.
- Do not invent tables or columns.
- Use SELECT or WITH queries only.
- If multiple tables are required, use the available relationship.
"""

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 300
        }
    )

    sql = response["message"]["content"]

    # Remove markdown code fences
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    # Token usage
    input_tokens = response.get("prompt_eval_count", 0)
    output_tokens = response.get("eval_count", 0)
    total_tokens = input_tokens + output_tokens

    print("\nGenerated SQL:")
    print(sql)

    print("\nToken Usage:")
    print("Input tokens:", input_tokens)
    print("Output tokens:", output_tokens)
    print("Total tokens:", total_tokens)

    # IMPORTANT: return updated state
    return {
        "schema": schema,
        "sql": sql,
        "llm_calls": state.get("llm_calls", 0) + 1,
        "input_tokens": state.get("input_tokens", 0) + input_tokens,
        "output_tokens": state.get("output_tokens", 0) + output_tokens,
        "total_tokens": state.get("total_tokens", 0) + total_tokens
    }

def validate_sql_node(state: AgentState):

    sql = state["sql"]

    print("\n[Node] Validate SQL")

    is_valid, message = validate_sql(sql)

    print("Validation Result:", is_valid)
    print("Validation Message:", message)

    return {
        "validation_result": is_valid,
        "validation_message": message
    }

    prompt = f"""
You are a SQL generation assistant.

Generate a DuckDB SQL query for the user's question.

Use ONLY the tables and columns provided below.

Schema:
{schema}

User question:
{question}

Rules:
- Generate only SQL.
- Do not explain the SQL.
- Do not invent tables or columns.
- Use SELECT or WITH queries only.
- If multiple tables are required, use the available relationship.
"""

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 300
        }
    )

    sql = response["message"]["content"]

    # Remove markdown code fences
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    # Token usage
    input_tokens = response.get("prompt_eval_count", 0)
    output_tokens = response.get("eval_count", 0)
    total_tokens = input_tokens + output_tokens

    print("\nGenerated SQL:")
    print(sql)

    print("\nToken Usage:")
    print("Input tokens:", input_tokens)
    print("Output tokens:", output_tokens)
    print("Total tokens:", total_tokens)

    return {
        "schema": schema,
        "sql": sql,
        "llm_calls": state.get("llm_calls", 0) + 1,
        "input_tokens": state.get("input_tokens", 0) + input_tokens,
        "output_tokens": state.get("output_tokens", 0) + output_tokens,
        "total_tokens": state.get("total_tokens", 0) + total_tokens
    }

def execute_sql_node(state: AgentState):

    sql = state["sql"]

    print("\n[Node] Execute SQL")
    print("Executing:")
    print(sql)

    con = duckdb.connect("data/telecom.duckdb")

    try:

        result = con.execute(sql).fetchdf()

        print("\nQuery Result:")
        print(result)

        return {
            "execution_result": result.to_string(index=False),
            "error": ""
        }

    except Exception as e:

        error_message = str(e)

        print("\nSQL Execution Error:")
        print(error_message)

        return {
            "execution_result": "",
            "error": error_message
        }

    finally:

        con.close()

def repair_sql_node(state: AgentState):

    print("\n[Node] Repair SQL")

    question = state["question"]
    sql = state["sql"]
    error = state["error"]
    schema = state["schema"]

    print("\nOriginal SQL:")
    print(sql)

    print("\nExecution Error:")
    print(error)

    prompt = f"""
You are a SQL debugging assistant.

The user asked:
{question}

The generated SQL was:

{sql}

The SQL execution produced this error:

{error}

Available schema:

{schema}

Generate a corrected DuckDB SQL query.

Rules:
- Return only SQL.
- Do not explain the SQL.
- Use only the tables and columns provided.
- Do not invent columns.
- Use SELECT or WITH only.
- Preserve the original business intent.
"""

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 300
        }
    )

    repaired_sql = response["message"]["content"]

    repaired_sql = repaired_sql.replace("```sql", "")
    repaired_sql = repaired_sql.replace("```", "")
    repaired_sql = repaired_sql.strip()

    input_tokens = response.get("prompt_eval_count", 0)
    output_tokens = response.get("eval_count", 0)
    total_tokens = input_tokens + output_tokens

    print("\nRepaired SQL:")
    print(repaired_sql)

    print("\nRepair Token Usage:")
    print("Input tokens:", input_tokens)
    print("Output tokens:", output_tokens)
    print("Total tokens:", total_tokens)

    return {
        "sql": repaired_sql,
        "repair_attempts": state.get("repair_attempts", 0) + 1,
        "llm_calls": state.get("llm_calls", 0) + 1,
        "input_tokens": state.get("input_tokens", 0) + input_tokens,
        "output_tokens": state.get("output_tokens", 0) + output_tokens,
        "total_tokens": state.get("total_tokens", 0) + total_tokens,
        "error": ""
    }

def execute_repaired_sql_node(state: AgentState):

    sql = state["sql"]

    print("\n[Node] Execute Repaired SQL")

    print("\nExecuting Repaired SQL:")
    print(sql)

    con = duckdb.connect("data/telecom.duckdb")

    try:

        result = con.execute(sql).fetchdf()

        print("\nRepaired Query Result:")
        print(result)

        return {
            "execution_result": result.to_string(index=False),
            "error": ""
        }

    except Exception as e:

        error_message = str(e)

        print("\nRepaired SQL Execution Error:")
        print(error_message)

        return {
            "execution_result": "",
            "error": error_message
        }

    finally:

        con.close()


def build_agent_graph():

    graph = StateGraph(AgentState)

    graph.add_node("retrieve_metadata", retrieve_metadata_node)
    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("validate_sql", validate_sql_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("repair_sql", repair_sql_node)
    graph.add_node("execute_repaired_sql", execute_repaired_sql_node)

    graph.add_edge(START, "retrieve_metadata")
    graph.add_edge("retrieve_metadata", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_edge("validate_sql", "execute_sql")

    graph.add_edge("execute_sql", "repair_sql")
    graph.add_edge("repair_sql", "execute_repaired_sql")

    graph.add_edge("execute_repaired_sql", END)

    return graph.compile()


"""if __name__ == "__main__":

    state: AgentState = {
        "question": "What is the total revenue by product?",
        "repair_attempts": 0,
        "llm_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }

    # Step 1 - Retrieve metadata
    state.update(
        retrieve_metadata_node(state)
    )

    # Step 2 - Generate SQL
    state.update(
        generate_sql_node(state)
    )

    # Step 3 - Validate SQL
    state.update(
        validate_sql_node(state)
    )

     # Step 4 - Execute SQL
    state.update(
        execute_sql_node(state)
    )

    state.update(
    execute_repaired_sql_node(state)
)

     # Test SQL Repair


state["error"] = 'Binder Error: Referenced column "amount" not found in FROM clause!'

state.update(
    repair_sql_node(state)
)

state.update(
    execute_repaired_sql_node(state)
)

print("\nUpdated Agent State:")
print(state) """

if __name__ == "__main__":

    app = build_agent_graph()

    initial_state: AgentState = {
        "question": "What is the total revenue by product?",
        "repair_attempts": 0,
        "llm_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }

    final_state = app.invoke(initial_state)

    print("\n========== FINAL STATE ==========")
    print(final_state)