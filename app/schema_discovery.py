import duckdb

DB_PATH = "data/telecom.duckdb"


def get_schema():
    con = duckdb.connect(DB_PATH)

    try:
        tables = con.execute("""
            SHOW TABLES
        """).fetchdf()

        schema = {}

        for table in tables["name"]:
            columns = con.execute(f"""
                DESCRIBE {table}
            """).fetchdf()

            schema[table] = columns[["column_name", "column_type"]].to_dict(
                orient="records"
            )

        return schema

    finally:
        con.close()


if __name__ == "__main__":
    schema = get_schema()

    for table, columns in schema.items():
        print(f"\nTable: {table}")

        for column in columns:
            print(f"  - {column['column_name']}: {column['column_type']}") 
            