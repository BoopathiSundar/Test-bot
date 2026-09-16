import chromadb
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent
CHROMA_FOLDER = BASE_DIR / "chroma_db"


# Connect to persistent ChromaDB
client = chromadb.PersistentClient(
    path=str(CHROMA_FOLDER)
)


# Open existing collection
collection = client.get_collection(
    name="documents"
)


def search_documents(query, n_results=3):
    """
    Search documents in ChromaDB using semantic similarity.
    """

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output = []

    for i, document in enumerate(documents):
        output.append({
            "document": document,
            "metadata": metadatas[i] if i < len(metadatas) else {},
            "distance": distances[i] if i < len(distances) else None
        })

    return output


if __name__ == "__main__":

    print("ChromaDB connected successfully")
    print("Collection:", collection.name)
    print("Document chunks:", collection.count())

    query = "What is MPOWER?"

    print("\nSearching for:", query)

    results = search_documents(query)

    for i, result in enumerate(results, start=1):
        print(f"\nRESULT {i}")
        print("-" * 60)
        print(result["document"])
        print("Metadata:", result["metadata"])
        print("Distance:", result["distance"])