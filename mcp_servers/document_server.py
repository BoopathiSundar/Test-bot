import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from chroma_service import search_documents
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Document Server")
UPLOAD_FOLDER = BASE_DIR / "uploads"


@mcp.tool()
def list_documents() -> str:
    """List all uploaded text documents."""

    if not UPLOAD_FOLDER.exists():
        return f"Upload folder does not exist: {UPLOAD_FOLDER}"

    files = list(UPLOAD_FOLDER.glob("*.txt"))

    if not files:
        return "No text documents found."

    return "\n".join(file.name for file in files)


@mcp.tool()
def read_document(filename: str) -> str:
    """Read an uploaded text document."""

    file_path = UPLOAD_FOLDER / filename

    if not file_path.exists():
        return f"Document not found: {filename}"

    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading document: {e}"


@mcp.tool()
def search_document(query: str) -> str:
    """Search uploaded documents using words from a natural-language question."""

    if not query or not query.strip():
        return "Please provide a search query."

    # Remove common question words
    stop_words = {
        "what",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "of",
        "about",
        "how",
        "why",
        "when",
        "where",
        "who",
        "which",
        "does",
        "do",
        "did",
        "can",
        "could",
        "would",
        "should",
        "tell",
        "me",
        "please",
        "explain"
    }

    # Convert question into useful search terms
    words = query.lower().split()

    search_terms = []

    for word in words:

        # Remove punctuation
        cleaned = word.strip(".,?!:;()[]{}\"'")

        if cleaned and cleaned not in stop_words:
            search_terms.append(cleaned)

    if not search_terms:
        return "No meaningful search terms found."

    if not UPLOAD_FOLDER.exists():
        return f"Upload folder does not exist: {UPLOAD_FOLDER}"

    files = list(UPLOAD_FOLDER.glob("*.txt"))

    if not files:
        return "No text documents found."

    results = []

    for file_path in files:

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )
        except Exception as e:

            results.append(
                f"{file_path.name}: Error reading file: {e}"
            )

            continue

        content_lower = content.lower()

        # Find terms that actually exist in document
        matched_terms = [
            term
            for term in search_terms
            if term in content_lower
        ]

        if not matched_terms:
            continue

        # Find the first matching term
        first_position = min(
            content_lower.find(term)
            for term in matched_terms
        )

        # Return surrounding context
        start = max(
            0,
            first_position - 500
        )

        end = min(
            len(content),
            first_position + 1500
        )

        context = content[start:end]

        results.append(
            f"""
--- {file_path.name} ---

Matched terms: {", ".join(matched_terms)}

{context}
"""
        )

    if not results:

        return (
            f'No results found for "{query}". '
            f'Try using a keyword from the document.'
        )

    return "\n".join(results)

@mcp.tool()
def semantic_search_document(query: str, n_results: int = 3) -> str:
    """
    Search uploaded documents using semantic similarity with ChromaDB.
    """

    try:
        results = search_documents(
            query=query,
            n_results=n_results
        )

        if not results:
            return f'No relevant documents found for "{query}".'

        output = []

        for i, result in enumerate(results, start=1):

            output.append(
                f"RESULT {i}\n"
                f"Source: {result['metadata'].get('source', 'unknown')}\n"
                f"Chunk: {result['metadata'].get('chunk', 'unknown')}\n"
                f"Distance: {result['distance']}\n"
                f"Content:\n{result['document']}"
            )

        return "\n\n" + ("\n" + "-" * 60 + "\n").join(output)

    except Exception as exc:
        return f"Semantic search failed: {exc}"

if __name__ == "__main__":
    import sys

    print("Starting Document MCP Server...", file=sys.stderr)
    print(f"Upload folder: {UPLOAD_FOLDER}", file=sys.stderr)

    mcp.run()   