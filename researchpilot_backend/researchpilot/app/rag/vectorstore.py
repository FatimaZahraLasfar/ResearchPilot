# app/rag/vectorstore.py
from langchain_community.vectorstores import Chroma
from app.rag.embedder import get_embeddings

DB_PATH = "./db"
COLLECTION_NAME = "researchpilot"

def get_vectorstore(reset: bool = False):
    embeddings = get_embeddings()

    vs = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    if reset:
        # ✅ Utiliser directement l'instance LangChain pour vider la collection
        # Évite tout conflit entre PersistentClient et Chroma LangChain
        try:
            vs._collection.delete(where={"source": {"$ne": "___"}})
        except Exception:
            # Si la collection est déjà vide, pas de problème
            pass

    return vs