# app/agents/planner.py
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

def planner_agent(state):
    query = state["query"]

    # Prompt corrigé : structure JSON précise et obligatoire
    prompt = f"""
You are a research planner. Analyze the query and return ONLY a valid JSON object.

Query: "{query}"

Return ONLY this JSON structure, nothing else, no markdown, no explanation:
{{
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "english_query": "the query translated to English if needed, otherwise same",
  "domain": "the main research domain (e.g. machine learning, health, NLP, computer vision, etc.)",
  "arxiv_category": "the most relevant arXiv category code among: cs.AI, cs.LG, cs.CL, cs.CV, cs.IR, cs.RO, stat.ML, q-bio, eess.IV, cs.NE",
  "strategy": "brief search strategy in one sentence"
}}

IMPORTANT: arxiv_category must be ONE of the codes listed above, pick the most relevant one for the query.
"""

    response = llm.invoke(prompt)
    raw = extract_text(response.content).strip()

    # Nettoyer les blocs markdown si présents
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()

    # Parser le JSON du planner
    try:
        parsed = json.loads(raw)
    except Exception:
        # Fallback si le JSON est invalide
        parsed = {
            "keywords": [query],
            "english_query": query,
            "domain": "general",
            "arxiv_category": "cs.AI",
            "strategy": "general search"
        }

    state["plan"] = parsed
    return state