# app/state.py
from typing import TypedDict, List, Dict, Any, Optional

class ResearchState(TypedDict):
    query: str
    plan: Dict[str, Any]
    articles: List[Dict[str, Any]]
    chunks: List[str]
    context: str
    synthesis: Dict[str, Any]
    critique: Dict[str, Any]
    report: str
    sources: List[Dict[str, Any]]
    citations: List[str]
    retry_count: int  # ✅ Compteur pour éviter la boucle infinie dans graph.py