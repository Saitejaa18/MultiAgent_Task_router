"""
LangGraph Workflow — Assembles the full Multi-Agent Router pipeline.

Graph structure:
  [START] → router → (code | research | summarize | general)
                ↓         ↓
           should_correct?
                ↓
         [correction_agent] → back to worker
                ↓
             [END]
"""

from langgraph.graph import StateGraph, END
from state.schema import AgentState
from agents.router import router_node, route_decision
from agents.code_agent import code_agent
from agents.research_agent import research_agent
from agents.summarizer_agent import summarizer_agent
from agents.general_agent import general_agent
from agents.correction_agent import correction_agent, should_correct, after_correction_route


def build_graph() -> StateGraph:
    """
    Builds and compiles the LangGraph multi-agent workflow.
    Returns a compiled graph ready for invocation.
    """
    graph = StateGraph(AgentState)

    # ── Register Nodes ────────────────────────────────────────────────
    graph.add_node("router", router_node)
    graph.add_node("code", code_agent)
    graph.add_node("research", research_agent)
    graph.add_node("summarize", summarizer_agent)
    graph.add_node("general", general_agent)
    graph.add_node("correction", correction_agent)

    # ── Entry Point ───────────────────────────────────────────────────
    graph.set_entry_point("router")

    # ── Router → Worker (Conditional) ────────────────────────────────
    # Only the relevant agent is activated — this is the token efficiency gain
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "code": "code",
            "research": "research",
            "summarize": "summarize",
            "general": "general",
        }
    )

    # ── Worker → Self-Correction or END ──────────────────────────────
    for worker in ["code", "research", "summarize", "general"]:
        graph.add_conditional_edges(
            worker,
            should_correct,
            {
                "correct": "correction",
                "done": END,
            }
        )

    # ── Correction → Back to Worker (Loop) ───────────────────────────
    graph.add_conditional_edges(
        "correction",
        after_correction_route,
        {
            "code": "code",
            "research": "research",
            "summarize": "summarize",
            "general": "general",
        }
    )

    return graph.compile()


# Singleton compiled graph — import this in main.py and app.py
task_router = build_graph()
