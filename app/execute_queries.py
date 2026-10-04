import duckdb

DB_PATH = "data/telecom.duckdb"


def execute_sql(sql):
    con = duckdb.connect(DB_PATH)

    try:
        result = con.execute(sql).fetchdf()
        return result
    finally:
        con.close()


if __name__ == "__main__":

    sql = """
        SELECT
            c.region,
            SUM(s.revenue) AS total_revenue
        FROM sales s
        JOIN customers c
            ON s.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY total_revenue DESC
    """

    result = execute_sql(sql)

    print(result)