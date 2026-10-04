import chromadb

VECTORSTORE_PATH = "vectorstore/chroma"

client = chromadb.PersistentClient(path=VECTORSTORE_PATH)

collection = client.get_collection(
    name="telecom_metadata"
)

#question = "What is the total revenue by product?"
question = "What customers are located in Dubai?"
results = collection.query(
    query_texts=[question],
    n_results=2
)

print("\nUser Question:")
print(question)

print("\nRetrieved Documents:")

for document in results["documents"][0]:
    print("\n---")
    print(document)