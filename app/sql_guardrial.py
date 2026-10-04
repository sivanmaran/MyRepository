import re


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
]


def validate_sql(sql):
    sql = sql.strip()

    # Remove markdown code fences if present
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE).strip()

    if ";" in sql[:-1]:
         return False, "Multiple SQL statements are not allowed."
    # Query must start with SELECT or WITH
    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Check for dangerous SQL commands
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql, re.IGNORECASE):
            return False, f"Forbidden SQL operation detected: {keyword}"

    return True, "SQL is valid."

def add_limit(sql, limit=1000):
    sql = sql.strip().rstrip(";")

    if re.search(r"\bLIMIT\s+\d+\b", sql, re.IGNORECASE):
        return sql + ";"

    return sql + f"\nLIMIT {limit};"


if __name__ == "__main__":

    # Test 1: Safe query
    safe_sql = """
    SELECT region, SUM(revenue)
    FROM sales
    GROUP BY region;
    """

    valid, message = validate_sql(safe_sql)

    print("Safe SQL:")
    print(valid, "-", message)

    # Test 2: Dangerous query
    dangerous_sql = """
    DROP TABLE customers
    """

    valid, message = validate_sql(dangerous_sql)

    print("\nDangerous SQL:")
    print(valid, "-", message)

    print("\nLimit Test:")

    sql = "SELECT * FROM sales"

    print(add_limit(sql))