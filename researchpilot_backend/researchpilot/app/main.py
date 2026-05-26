# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI(title="ResearchPilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class QueryRequest(BaseModel):
    query: str


@app.post("/research")
def run_research(req: QueryRequest):
    state = {
        "query": req.query,
        "plan": {},
        "articles": [],
        "chunks": [],
        "context": "",
        "synthesis": {},
        "critique": {},
        "report": "",
        "sources": [],
        "citations": [],
        "retry_count": 0  # ✅ Initialiser le compteur de tentatives
    }

    try:
        result = graph.invoke(state)
    except Exception as exc:
        message = str(exc)
        if "RESOURCE_EXHAUSTED" in message or "quota" in message.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Quota API épuisé. Veuillez patienter quelques minutes "
                    "ou utiliser une clé avec du quota disponible."
                ),
            ) from exc
        raise HTTPException(
            status_code=503,
            detail=f"Pipeline échoué : {message}",
        ) from exc

    return {
        "report": result["report"],
        "synthesis": result["synthesis"],
        "critique": result["critique"],
        "sources": result.get("sources", []),
        "citations": result.get("citations", [])
    }