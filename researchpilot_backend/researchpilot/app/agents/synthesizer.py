# app/agents/synthesizer.py
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)

def extract_text(content):
    """Extrait le texte brut d'une réponse LLM (string ou liste de blocs)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts)
    return str(content)

def synthesizer_agent(state):
    query = state["query"]
    sources = state.get("sources", [])
    context = state.get("context", "")

    # ✅ Construire la liste des sources avec numérotation
    sources_text = ""
    sources_valides = []

    if sources:
        sources_text = "SOURCES DISPONIBLES (utilise uniquement celles liées à la requête) :\n"
        for i, source in enumerate(sources, 1):
            sources_text += (
                f"\n[{i}] Titre: {source['title']}\n"
                f"    Auteurs: {', '.join(source['authors'])}\n"
                f"    URL: {source['url']}\n"
                f"    Publié: {source['published']}\n"
                f"    Résumé: {source['summary'][:300]}\n"
            )
        sources_valides = sources

    # ✅ Si pas de contexte RAG, signaler clairement
    if not context or not sources:
        state["synthesis"] = {
            "text": (
                f"Aucun article académique pertinent n'a été trouvé sur arXiv "
                f"pour la requête : **{query}**.\n\n"
                f"Veuillez reformuler votre requête avec des termes plus précis en anglais, "
                f"par exemple : *Retrieval Augmented Generation* au lieu de *RAG*."
            )
        }
        state["citations"] = []
        return state

    prompt = f"""
Tu es un chercheur académique. En te basant STRICTEMENT sur le contexte et les sources ci-dessous, rédige une synthèse structurée en FRANÇAIS au format Markdown.

REQUÊTE : "{query}"

RÈGLES ABSOLUES :
1. Reste STRICTEMENT centré sur la requête "{query}". 
2. Si une source ne parle PAS du sujet "{query}", IGNORE-LA COMPLÈTEMENT. Ne la cite pas.
3. Cite OBLIGATOIREMENT avec [1], [2], etc. chaque affirmation importante.
4. Ne génère AUCUNE information qui ne vient pas des sources fournies.
5. Rédige UNIQUEMENT en FRANÇAIS. Aucune phrase en anglais.
6. Si les sources sont insuffisantes pour une section, dis-le explicitement.

STRUCTURE OBLIGATOIRE :

### Tendances Clés
(Paragraphes sur les grandes tendances liées à "{query}", avec citations [N])

### Auteurs Principaux et Sources
(Liste des auteurs avec leurs travaux et liens arXiv directs)

### Lacunes de Recherche
(Ce qui manque ou mériterait d'être approfondi sur "{query}")

{sources_text}

CONTEXTE EXTRAIT DES ARTICLES :
{context}
"""

    res = llm.invoke(prompt)
    synthesis_text = extract_text(res.content)

    state["synthesis"] = {"text": synthesis_text}

    # Extraire les numéros de citations utilisés
    citations = re.findall(r'\[\d+\]', synthesis_text)
    state["citations"] = citations

    return state