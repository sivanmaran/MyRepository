import duckdb

DB_PATH = "data/telecom.duckdb"

con = duckdb.connect(DB_PATH)

# Create customers table
con.execute("""
    CREATE OR REPLACE TABLE customers AS
    SELECT *
    FROM read_csv_auto('data/customer.csv')
""")

# Create sales table
con.execute("""
    CREATE OR REPLACE TABLE sales AS
    SELECT *
    FROM read_csv_auto('data/sales.csv')
""")

print("Tables created successfully!")

print("\nCustomers:")
print(con.execute("""
    SELECT *
    FROM customers
    LIMIT 5
""").fetchdf())

print("\nSales:")
print(con.execute("""
    SELECT *
    FROM sales
    LIMIT 5
""").fetchdf())

con.close()