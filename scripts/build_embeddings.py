import os

from backend.config.settings import client_openai

# Loading API key from secret.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import chromadb

CHROMA_PATH = os.path.join(BASE_DIR, "data/chroma_db")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="ttc_docs")

DOCS_PATH = os.path.join(BASE_DIR, "data/docs/ttc_docs")

# --- Helper: infer topic from filename ---
def get_topic(filename):
    if filename.startswith("line"):
        return "subway_line"
    elif filename.startswith("route"):
        return "route_info"
    elif "presto" in filename:
        return "presto"
    elif "fare" in filename:
        return "fare_rules"
    elif "policy" in filename:
        return "policy"
    elif "faq" in filename:
        return "faq"
    else:
        return "general"
    
# --- Helper: chunk text ---
def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap

    return chunks


# --- Main ---
all_docs = []
all_meta = []
all_ids = []
    
for filename in os.listdir(DOCS_PATH):
    if not filename.endswith(".txt"):
        continue
    
    filepath = os.path.join(DOCS_PATH, filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        
    chunks = chunk_text(text)
    topic = get_topic(filename)
    
    for idx, chunk in enumerate(chunks):
        all_docs.append(chunk)
        all_meta.append({
            "source": filename,
            "topic": topic,
            "chunk_id": idx
        })
        all_ids.append(f"{filename}_{idx}")
        
# --- Create embeddings ---
embeddings = client_openai.embeddings.create(
    model="text-embedding-3-small",
    input=all_docs
).data

embedding_vectors = [e.embedding for e in embeddings]

# --- Store in ChromaDB ---
collection.add(
    documents=all_docs,
    metadatas=all_meta,
    ids=all_ids,
    embeddings=embedding_vectors
)

print("Embeddings stored successfully.")
