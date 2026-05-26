# app/agents/critic.py
import os
import re
import json
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

def critic_agent(state):
    query = state.get("query", "")
    synthesis_text = state.get("synthesis", {}).get("text", "")
    sources = state.get("sources", [])

    # ✅ Préparer la liste des titres de sources pour que le Critic puisse juger leur pertinence
    sources_titles = ""
    if sources:
        sources_titles = "SOURCES UTILISÉES :\n"
        for i, source in enumerate(sources, 1):
            sources_titles += f"  [{i}] {source.get('title', 'Titre inconnu')}\n"
    else:
        sources_titles = "SOURCES UTILISÉES : Aucune source académique trouvée.\n"

    prompt = f"""
Tu es un évaluateur académique rigoureux. Évalue cette synthèse de recherche sur une échelle de 0 à 10.
IMPORTANT : Ton retour (feedback) DOIT être rédigé en FRANÇAIS.

REQUÊTE ORIGINALE : "{query}"

{sources_titles}

SYNTHÈSE À ÉVALUER :
{synthesis_text}

CRITÈRES D'ÉVALUATION (pondérés) :
1. Pertinence des sources par rapport à la requête "{query}" (3 points)
   - Si des sources hors-sujet sont citées, enlève des points
   - Si aucune source pertinente n'est trouvée, score maximum = 4
2. Qualité et précision des citations [1], [2], etc. (2 points)
3. Structure et clarté de la synthèse (2 points)
4. Identification correcte des lacunes de recherche (2 points)
5. Qualité du français et fluidité (1 point)

Réponds UNIQUEMENT avec un JSON valide (sans markdown, sans ```json) :
{{"score": int, "feedback": "str"}}
"""

    res = llm.invoke(prompt)
    raw = extract_text(res.content).strip()

    # Nettoyer les blocs markdown si présents
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()

    try:
        parsed = json.loads(raw)
        score = int(parsed.get("score", 5))
        feedback = parsed.get("feedback", raw)
    except Exception:
        score = 5
        feedback = raw

    state["critique"] = {
        "score": score,
        "feedback": feedback
    }

    return state