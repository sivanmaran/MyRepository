import chromadb

VECTORSTORE_PATH = "vectorstore/chroma"

client = chromadb.PersistentClient(
    path=VECTORSTORE_PATH
)

print("Available Collections:")
print(client.list_collections())

collection = client.get_collection(
    name="telecom_metadata"
)


def retrieve_metadata(question, top_k=1):

    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    tables = []

    for metadata, document in zip(metadatas, documents):

        table = {
            "table": metadata["table"],
            "description": "",
            "columns": {}
        }

        lines = document.splitlines()

        for line in lines:

            if line.startswith("Description:"):
                table["description"] = line.replace(
                    "Description:", ""
                ).strip()

            elif line.startswith("- "):

                column_text = line[2:]

                column, description = column_text.split(
                    ":", 1
                )

                table["columns"][column.strip()] = description.strip()

        tables.append(table)

    # Add customers when the question requires customer attributes
    customer_columns = [
        "region",
        "segment",
        "customer_name",
        "status"
    ]

    question_lower = question.lower()

    if any(column in question_lower for column in customer_columns):

        if not any(table["table"] == "customers" for table in tables):

            customers_result = collection.get(
                where={"table": "customers"},
                include=["documents", "metadatas"]
            )

            if customers_result["documents"]:

                document = customers_result["documents"][0]
                metadata = customers_result["metadatas"][0]

                table = {
                    "table": metadata["table"],
                    "description": "",
                    "columns": {}
                }

                lines = document.splitlines()

                for line in lines:

                    if line.startswith("Description:"):
                        table["description"] = line.replace(
                            "Description:", ""
                        ).strip()

                    elif line.startswith("- "):

                        column_text = line[2:]

                        column, description = column_text.split(
                            ":", 1
                        )

                        table["columns"][column.strip()] = description.strip()

                tables.append(table)

    return {
        "tables": tables,
        "relationships": """
sales.customer_id = customers.customer_id
"""
    }

if __name__ == "__main__":

    question = input("\nAsk your question: ")

    results = retrieve_metadata(question,top_k=1)

    print("\nRetrieved Metadata:")

    for metadata, document in zip(
        results["metadatas"],
        results["documents"]
    ):
        print("\n---")
       # print("Table:", metadata["table"])
        print(document)