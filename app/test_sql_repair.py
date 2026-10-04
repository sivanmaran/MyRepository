import duckdb

from sql_guardrial import validate_sql
from sql_repair import repair_sql


DB_PATH = "data/telecom.duckdb"

question = "What is the total revenue by region?"

# Intentionally incorrect column name
bad_sql = """
SELECT region, SUM(amount) AS total_revenue
FROM sales
JOIN customers
    ON sales.customer_id = customers.customer_id
GROUP BY region;
"""

schema = """
sales:
- sale_id
- customer_id
- sale_date
- product
- revenue

customers:
- customer_id
- customer_name
- region
- segment
- status
"""

con = duckdb.connect(DB_PATH)

try:

    print("\nOriginal SQL:")
    print(bad_sql)

    valid, message = validate_sql(bad_sql)

    print("\nGuardrail:")
    print(message)

    try:

        result = con.execute(bad_sql).fetchdf()

        print("\nQuery Result:")
        print(result)

    except Exception as e:

        print("\nSQL Execution Error:")
        print(e)

        print("\nAttempting SQL Repair...")

        repaired_sql = repair_sql(
            question,
            bad_sql,
            str(e),
            schema
        )

        print("\nRepaired SQL:")
        print(repaired_sql)

        valid, message = validate_sql(repaired_sql)

        print("\nRepaired SQL Guardrail:")
        print(message)

        if not valid:
            print("\nRepaired SQL rejected.")
            exit()

        result = con.execute(repaired_sql).fetchdf()

        print("\nRepaired Query Result:")
        print(result)

finally:
    con.close()