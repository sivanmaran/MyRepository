import ollama
import duckdb
import re
from sql_guardrial import validate_sql,add_limit
#from metadata_retriever import retrieve_metadata
from vector_retriever import retrieve_metadata
from sql_repair import repair_sql



DB_PATH = "data/telecom.duckdb"

schema = """

"""

#question = "What is the total revenue by region?"
question = input("\nAsk your question: ")

metadata_context = retrieve_metadata(question)

relevant_metadata = metadata_context["tables"]
relationships = metadata_context["relationships"]

schema = ""

for table in relevant_metadata:
    schema += f"\n{table['table']}:\n"

    for column, description in table["columns"].items():
        schema += f"- {column}\n"

schema += "\nRelationship:\n"
schema += relationships

print("\nDynamic Schema:")
print(schema)

print("\nRetrieved Metadata:")

for table in relevant_metadata:
    print(f"\nTable: {table['table']}")
    print(f"Description: {table['description']}")

    for column, description in table["columns"].items():
        print(f"  - {column}: {description}")


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
- If the question requires columns from multiple tables, use the relationship provided.
- Use JOIN when required.
- For text filters, use case-insensitive matching with LOWER(column) = LOWER('value').
- Generate SELECT or WITH queries only.
"""

response = ollama.chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

sql = response["message"]["content"]

# Remove Markdown code fences
sql = response["message"]["content"]

sql = sql.replace("```sql", "")
sql = sql.replace("```", "")
sql = sql.strip()
#sql = sql.replace("revenue", "amount")


sql = add_limit(sql)

print("\nGenerated SQL:")
print(sql)

# Validate SQL before execution
valid, message = validate_sql(sql)

print("\nSQL Guardrail:")
print(message)

if not valid:
    print("Query rejected.")
    exit()


# Execute SQL
con = duckdb.connect(DB_PATH)

try:

    try:
        result = con.execute(sql).fetchdf()

    except Exception as e:

        print("\nSQL Execution Error:")
        print(e)

        print("\nAttempting SQL Repair...")

        repaired_sql = repair_sql(
            question,
            sql,
            str(e),
            schema
        )

        repaired_sql = add_limit(repaired_sql)

        print("\nRepaired SQL:")
        print(repaired_sql)

        valid, message = validate_sql(repaired_sql)

        print("\nRepaired SQL Guardrail:")
        print(message)

        if not valid:
            print("\nRepaired SQL rejected by guardrail.")
            exit()

        result = con.execute(repaired_sql).fetchdf()

    print("\nQuery Result:")
    print(result)

finally:
    con.close()

result_text = result.to_string(index=False)

answer_prompt = f"""
You are a data analyst.

The user asked:
{question}

The SQL query returned this result:

{result_text}

Answer the user's question using the result.

Rules:
- Be concise.
- Mention important numbers.
- Include AED when referring to revenue.
- Do not show SQL.
"""

answer_response = ollama.chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": answer_prompt
        }
    ]
)

answer = answer_response["message"]["content"]

print("\nAI Answer:")
print(answer)