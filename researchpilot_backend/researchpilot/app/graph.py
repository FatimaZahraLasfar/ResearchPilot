# app/graph.py
from langgraph.graph import StateGraph, END
from app.state import ResearchState

from app.agents.planner import planner_agent
from app.agents.collector import collector_agent
from app.agents.rag import rag_agent
from app.agents.synthesizer import synthesizer_agent
from app.agents.critic import critic_agent
from app.agents.report import report_agent


def build_graph():

    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_agent)
    graph.add_node("collector", collector_agent)
    graph.add_node("rag", rag_agent)
    graph.add_node("synth", synthesizer_agent)
    graph.add_node("critic", critic_agent)
    graph.add_node("report", report_agent)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "collector")
    graph.add_edge("collector", "rag")
    graph.add_edge("rag", "synth")
    graph.add_edge("synth", "critic")

    # ✅ Boucle critique avec protection contre les boucles infinies
    # Sans le compteur, si le score reste < 7 indéfiniment,
    # le pipeline tourne en boucle sans jamais s'arrêter.
    def route_after_critic(state):
        score = state["critique"]["score"]
        retry_count = state.get("retry_count", 0)

        # Maximum 2 tentatives, ensuite forcer la génération du rapport
        if score >= 7 or retry_count >= 2:
            return "report"
        else:
            return "rag"

    graph.add_conditional_edges("critic", route_after_critic)
    graph.add_edge("report", END)

    return graph.compile()