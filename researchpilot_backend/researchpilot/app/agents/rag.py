# app/agents/rag.py
from app.rag.vectorstore import get_vectorstore
from app.rag.loader import chunk_text

def rag_agent(state):
    # ✅ CORRECTION PRINCIPALE : réinitialiser le vectorstore à chaque nouvelle recherche
    # Sans ce reset, ChromaDB garde les chunks des recherches précédentes
    # et le RAG remonte des résultats d'anciennes requêtes (ex: "Machine learning"
    # quand on cherche "RAG"), ce qui explique le "0 article trouvé" mais une
    # synthèse basée sur d'anciens articles.
    vs = get_vectorstore(reset=True)

    all_chunks = []

    for article in state["articles"]:
        chunks = chunk_text(article["raw"])
        if chunks:
            vs.add_texts(chunks)
            all_chunks.extend(chunks)

    state["chunks"] = all_chunks

    # ✅ Vérifier qu'on a des chunks avant de faire la recherche
    if not all_chunks:
        state["context"] = ""
        return state

    # Recherche de similarité avec la requête
    results = vs.similarity_search(state["query"], k=5)

    state["context"] = "\n\n".join([r.page_content for r in results])

    return state