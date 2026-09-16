import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
CHROMA_FOLDER = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_FOLDER)
)

collection = client.get_or_create_collection(
    name="documents"
)

file_path = UPLOAD_FOLDER / "tobacco.txt"

if not file_path.exists():
    print(f"File not found: {file_path}")
    exit()

text = file_path.read_text(encoding="utf-8")

chunk_size = 1000
chunks = []

for i in range(0, len(text), chunk_size):
    chunk = text[i:i + chunk_size].strip()

    if chunk:
        chunks.append(chunk)

ids = [
    f"tobacco_chunk_{i}"
    for i in range(len(chunks))
]

metadatas = [
    {
        "source": "tobacco.txt",
        "chunk": i
    }
    for i in range(len(chunks))
]

collection.upsert(
    ids=ids,
    documents=chunks,
    metadatas=metadatas
)

print("Collection created successfully")
print("Collection name:", collection.name)
print("Number of chunks:", collection.count())