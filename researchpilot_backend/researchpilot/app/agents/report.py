# app/agents/report.py
from datetime import datetime
import re


def _clean_pdf_text(text: str) -> str:
    """Nettoie le texte pour un rendu lisible en PDF / texte brut."""
    if not text:
        return ""
    text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
    text = re.sub(r'###\s*', '\n\n', text)
    text = re.sub(r'##\s*', '\n\n', text)
    text = re.sub(r'#\s*', '\n\n', text)
    text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()


def _safe_authors(source):
    authors = source.get("authors", [])
    return ", ".join(authors) if authors else "Auteurs non renseignés"


def _safe_title(source):
    return (source.get("title") or "Titre inconnu").strip()


def _safe_published(source):
    raw = source.get("published", "Date inconnue")
    # Simplifier le format de date ISO (2024-01-15T00:00:00Z → 2024-01-15)
    if "T" in raw:
        return raw.split("T")[0]
    return raw


def _safe_url(source):
    return source.get("url", "")


def _safe_summary(source):
    summary = source.get("summary", "Aucun extrait disponible.")
    if len(summary) > 450:
        return summary[:450] + "..."
    return summary


def _render_sources(sources):
    if not sources:
        return "Aucune source academique trouvee."

    lines = [f"Nombre d'articles utilises : {len(sources)}\n"]
    for i, source in enumerate(sources, 1):
        lines.append(f"[{i}] {_safe_title(source)}")
        lines.append(f"Auteurs : {_safe_authors(source)}")
        lines.append(f"Date    : {_safe_published(source)}")
        url = _safe_url(source)
        if url:
            lines.append(f"Lien    : {url}")
        lines.append(f"Extrait : {_safe_summary(source)}")
        lines.append("-" * 70)
    return "\n".join(lines)


def _render_proofs(sources):
    if not sources:
        return "Aucune preuve source disponible."

    lines = []
    for i, source in enumerate(sources, 1):
        lines.append(f"Preuve {i} : {_safe_title(source)}")
        lines.append(f"Auteurs  : {_safe_authors(source)}")
        lines.append(f"Extrait  : {_safe_summary(source)}")
        url = _safe_url(source)
        if url:
            lines.append(f"Lien     : {url}")
        lines.append("-" * 70)
    return "\n".join(lines)


def report_agent(state):
    synthesis = state.get("synthesis", {})
    critique = state.get("critique", {})
    sources = state.get("sources", [])
    plan = state.get("plan", {})

    synthesis_text = _clean_pdf_text(synthesis.get("text", ""))
    feedback_text = _clean_pdf_text(critique.get("feedback", ""))

    # Infos du plan pour le rapport
    domain = plan.get("domain", "Non specifie")
    arxiv_category = plan.get("arxiv_category", "Non specifie")

    report = f"""
RAPPORT DE RECHERCHE - ResearchPilot
====================================

REQUETE INITIALE :
{state.get('query', '')}

DOMAINE DETECTE    : {domain}
CATEGORIE ARXIV    : {arxiv_category}

RESUME EXECUTIF :
Ce rapport a ete genere a partir de {len(sources)} article(s) trouve(s) sur arXiv.
Il vise a presenter les resultats de facon lisible, verifiable et exploitable.

SYNTHESE STRUCTUREE
===================
{synthesis_text}

PREUVES D'ANCRAGE
=================
{_render_proofs(sources)}

SOURCES UTILISEES
=================
{_render_sources(sources)}

EVALUATION DE LA QUALITE
========================
Note Critique : {critique.get('score', 'N/A')}/10
Feedback      : {feedback_text}

RAPPORT GENERE LE : {datetime.now().strftime('%d/%m/%Y a %H:%M:%S')}
"""

    state["report"] = report
    return state