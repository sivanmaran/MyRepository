import duckdb

DB_PATH = "data/telecom.duckdb"

con = duckdb.connect(DB_PATH)

print("Customers count:")
print(con.execute("""
    SELECT COUNT(*) AS customer_count
    FROM customers
""").fetchdf())

print("\nSales count:")
print(con.execute("""
    SELECT COUNT(*) AS sales_count
    FROM sales
""").fetchdf())

print("\nRevenue by region:")
print(con.execute("""
    SELECT
        c.region,
        SUM(s.revenue) AS total_revenue
    FROM sales s
    JOIN customers c
        ON s.customer_id = c.customer_id
    GROUP BY c.region
    ORDER BY total_revenue DESC
""").fetchdf())

con.close()