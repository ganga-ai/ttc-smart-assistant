import os
from openai import OpenAI
#from dotenv import load_dotenv

from backend.config.settings import client_openai

import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_PATH = os.path.join(BASE_DIR, "data/chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(name="ttc_docs")

def ask_ttc_question(question: str) -> str:
    try:
        # 1. Embed the query
        embedding = client_openai.embeddings.create(
            model="text-embedding-3-small",
            input=[question]
        ).data[0].embedding

       # print(collection.count())

        # 2. Retrieve top chunks
        results = collection.query(
            query_embeddings=[embedding],
            n_results=3
        )

        docs = results.get("documents", [[]])[0]

        if not docs:
            return "I don't know based on the available data."

        # 3. Build context
        context = "\n\n".join(docs)

        # 4. Ask LLM
        prompt = f"""
        Answer the question using ONLY the context below.
        If the answer is not present, say you don't know.

        Context:
        {context}

        Question:
        {question}
        """

        response = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"