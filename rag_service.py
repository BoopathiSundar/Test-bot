import requests

from chroma_service import search_documents
from ollama_config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


def ask_rag(question, n_results=3):

    print("\n1. Searching ChromaDB...")

    results = search_documents(
        query=question,
        n_results=n_results
    )

    print("Retrieved results:", len(results))

    if not results:
        return "The answer is not available in the uploaded documents."

    # Build context
    context_parts = []

    for result in results:
        document = result.get("document", "")
        source = result.get("metadata", {}).get("source", "unknown")

        context_parts.append(
            f"Source: {source}\n{document}"
        )

    context = "\n\n---\n\n".join(context_parts)

    print("\n2. Context retrieved:")
    print(context)

    # Simple chat request
    messages = [
        {
            "role": "system",
            "content": "Answer questions using the supplied document context."
        },
        {
            "role": "user",
            "content": (
                "DOCUMENT:\n\n"
                + context
                + "\n\nQUESTION:\n"
                + question
                + "\n\nAnswer the question."
            )
        }
    ]

    print("\n3. Sending request to Ollama...")
    print("URL:", OLLAMA_URL)
    print("MODEL:", OLLAMA_MODEL)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        },
        timeout=OLLAMA_TIMEOUT
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    print("\n4. Raw Ollama response:")
    print(data)

    message = data.get("message")

    if not message:
        return "No message returned by Ollama."

    answer = message.get("content", "")

    print("\n5. Answer length:", len(answer))

    return answer


if __name__ == "__main__":

    question = "What is MPOWER?"

    print("=" * 70)
    print("RAG TEST")
    print("=" * 70)

    answer = ask_rag(question)

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)
    print(answer)