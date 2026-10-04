import ollama


def repair_sql(question, sql, error, schema):
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
        ]
    )

    repaired_sql = response["message"]["content"]

    repaired_sql = repaired_sql.replace("```sql", "")
    repaired_sql = repaired_sql.replace("```", "")
    repaired_sql = repaired_sql.strip()

    return repaired_sql