# app/agents/collector.py
import time
import requests
import certifi
import xml.etree.ElementTree as ET

def parse_arxiv_xml(xml_text: str) -> tuple:
    """Extrait titre, résumé, auteurs, URL de chaque article du XML arXiv.
    Retourne: (texte_brut, liste_sources)
    """
    try:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(xml_text)
        entries = root.findall("atom:entry", ns)
        if not entries:
            return "", []

        parts = []
        sources = []

        for entry in entries:
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
            published = entry.findtext("atom:published", default="", namespaces=ns).strip()

            # Récupérer l'URL arXiv (lien abs, pas PDF)
            arxiv_url = ""
            for link in entry.findall("atom:link", ns):
                if link.get("rel") == "alternate":
                    arxiv_url = link.get("href", "")
                    break
            # Fallback : convertir le lien PDF en abs
            if not arxiv_url:
                for link in entry.findall("atom:link", ns):
                    if link.get("title") == "pdf":
                        href = link.get("href", "")
                        arxiv_url = href.replace("/pdf/", "/abs/").replace(".pdf", "")
                        break

            # Récupérer les auteurs
            authors = [
                a.findtext("atom:name", default="", namespaces=ns)
                for a in entry.findall("atom:author", ns)
            ]

            source_entry = {
                "title": title,
                "authors": authors,
                "url": arxiv_url,
                "published": published,
                "summary": summary
            }
            sources.append(source_entry)

            parts.append(
                f"Titre : {title}\n"
                f"Auteurs : {', '.join(authors)}\n"
                f"URL : {arxiv_url}\n"
                f"Publié : {published}\n"
                f"Résumé : {summary}"
            )

        return "\n\n---\n\n".join(parts), sources
    except ET.ParseError:
        return "", []


def collector_agent(state):
    raw_query = state["query"]

    # ✅ Lire le plan du Planner pour utiliser la catégorie et la query anglaise
    plan = state.get("plan", {})
    arxiv_category = plan.get("arxiv_category", "")
    english_query = plan.get("english_query", raw_query)
    keywords = plan.get("keywords", [raw_query])

    # Construire la query arXiv avec les mots-clés ET la catégorie
    keywords_str = " OR ".join(keywords[:3])  # Max 3 mots-clés

    if arxiv_category:
        # ✅ Filtre par catégorie : évite les articles hors-domaine (ex: astrophysique)
        search_query = f"cat:{arxiv_category} AND all:({english_query})"
    else:
        search_query = f"all:({english_query})"

    url = (
        f"https://export.arxiv.org/api/query"
        f"?search_query={requests.utils.quote(search_query)}"
        f"&start=0&max_results=8&sortBy=relevance&sortOrder=descending"
    )

    for attempt in range(3):
        try:
            res = requests.get(url, verify=certifi.where(), timeout=15)
            if res.status_code == 200:
                content, sources = parse_arxiv_xml(res.text)

                # ✅ Vérifier qu'on a bien des articles
                if sources:
                    state["articles"] = [{"source": "arxiv", "raw": content}]
                    state["sources"] = sources
                    return state

                # Si pas de résultats avec catégorie, réessayer sans filtre catégorie
                if arxiv_category:
                    fallback_url = (
                        f"https://export.arxiv.org/api/query"
                        f"?search_query={requests.utils.quote(f'all:({english_query})')}"
                        f"&start=0&max_results=8&sortBy=relevance&sortOrder=descending"
                    )
                    res2 = requests.get(fallback_url, verify=certifi.where(), timeout=15)
                    if res2.status_code == 200:
                        content2, sources2 = parse_arxiv_xml(res2.text)
                        if sources2:
                            state["articles"] = [{"source": "arxiv", "raw": content2}]
                            state["sources"] = sources2
                            return state

            elif res.status_code == 429:
                time.sleep(5 * (attempt + 1))

        except requests.RequestException:
            time.sleep(3)

    # Fallback total : aucun article trouvé
    state["articles"] = [{
        "source": "fallback",
        "raw": (
            f"Aucun article trouvé pour la requête : {raw_query}. "
            f"Génère une synthèse basée sur tes connaissances générales sur ce sujet."
        )
    }]
    state["sources"] = []
    return state