"""
Router Agent — Classifies incoming tasks using Groq Llama 3 8B (fast & cheap).
Uses a structured prompt to classify into: code | research | summarize | general
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state.schema import AgentState

load_dotenv()


# Use the fastest, cheapest model just for routing decisions
router_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,         # Deterministic classification
    max_tokens=20,         # Only need a single-word answer -- saves tokens
)

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a task classifier. Your ONLY job is to read a user's task and respond with exactly one word 
from this list: code, research, summarize, general.

Rules:
- code       → user wants code written, debugged, explained, or reviewed
- research   → user wants information, facts, comparisons, or web-style answers
- summarize  → user wants a text, document, or content condensed/summarized  
- general    → anything else (chit-chat, opinions, greetings, etc.)

Respond with ONLY the single classification word. No punctuation. No explanation."""
    ),
    ("human", "Task: {task}")
])


def router_node(state: AgentState) -> AgentState:
    """
    Router agent node. Classifies the task and returns updated state.
    Token-efficient: uses max_tokens=20 and a mini model.
    """
    chain = ROUTER_PROMPT | router_llm
    response = chain.invoke({"task": state["task"]})
    task_type = response.content.strip().lower()

    # Validate classification, fallback to "general"
    valid_types = {"code", "research", "summarize", "general"}
    if task_type not in valid_types:
        task_type = "general"

    log_entry = f"[ROUTER] Classified task as: '{task_type}'"
    return {
        **state,
        "task_type": task_type,
        "messages": state.get("messages", []) + [log_entry],
    }


def route_decision(state: AgentState) -> str:
    """
    Conditional edge function — returns the next node name based on task_type.
    LangGraph uses this to determine which agent to activate.
    """
    return state.get("task_type", "general")
