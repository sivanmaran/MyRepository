import chromadb
import json
import os

METADATA_PATH = "metadata"
VECTORSTORE_PATH = "vectorstore/chroma"

client = chromadb.PersistentClient(path=VECTORSTORE_PATH)

collection = client.get_or_create_collection(
    name="telecom_metadata"
)

for filename in os.listdir(METADATA_PATH):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(METADATA_PATH, filename)

    with open(filepath, "r") as file:
        metadata = json.load(file)

    table = metadata["table"]

    text = (
        f"Table: {table}\n"
        f"Description: {metadata['description']}\n"
        f"Columns:\n"
    )

    for column, description in metadata["columns"].items():
        text += f"- {column}: {description}\n"

    collection.upsert(
        ids=[table],
        documents=[text],
        metadatas=[{"table": table}]
    )

print("Vector store created successfully!")

print(f"Documents stored: {collection.count()}")

print("\nStored metadata:")

results = collection.get(
    include=["documents", "metadatas"]
)

for i, document in enumerate(results["documents"]):
    print("\n---")
    print(results["metadatas"][i])
    print(document)