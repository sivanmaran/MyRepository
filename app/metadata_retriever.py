import json
import os

METADATA_PATH = "metadata"

RELATIONSHIPS = """
sales.customer_id = customers.customer_id
"""



def load_metadata():
    metadata = []

    for filename in os.listdir(METADATA_PATH):
        if filename.endswith(".json"):
            filepath = os.path.join(METADATA_PATH, filename)

            with open(filepath, "r") as file:
                metadata.append(json.load(file))

    return metadata


def retrieve_metadata(question):
    metadata = load_metadata()

    question_words = question.lower().split()

    relevant_tables = []

    for table in metadata:

        table_text = (
            table["table"]
            + " "
            + table["description"]
            + " "
            + " ".join(table["columns"].keys())
            + " "
            + " ".join(table["columns"].values())
        ).lower()

        if any(word in table_text for word in question_words):
            relevant_tables.append(table)

    # If sales is relevant, include customers because they are related
    table_names = [table["table"] for table in relevant_tables]

    if "sales" in table_names and "customers" not in table_names:
        for table in metadata:
            if table["table"] == "customers":
                relevant_tables.append(table)

    return {
    "tables": relevant_tables,
    "relationships": RELATIONSHIPS
}


if __name__ == "__main__":

    question = "What is the total revenue by region?"

    results = retrieve_metadata(question)

    print("User Question:")
    print(question)

    print("\nRelevant Metadata:")

    for table in results["tables"]:
        print(f"\nTable: {table['table']}")
        print(f"Description: {table['description']}")

        for column, description in table["columns"].items():
            print(f"  - {column}: {description}")

    print("\nRelationships:")
    print(results["relationships"])