"""
Research Agent -- Handles information retrieval, Q&A, comparisons, and factual queries.
Uses Groq Llama 3 70B for fast, comprehensive research responses.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state.schema import AgentState

load_dotenv()


research_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.4,
)

RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert research analyst and knowledge specialist.
Your responsibilities:
- Provide accurate, well-structured, and comprehensive answers
- Use clear headings and bullet points where appropriate
- Cite reasoning and provide context for your answers
- Compare and contrast options when relevant
- Flag any uncertainty clearly

If given correction notes from a previous attempt, incorporate that feedback.
Format your response in a clear, readable markdown structure."""
    ),
    ("human", "Research Task: {task}\n\nCorrection Notes (if any): {correction_notes}")
])


def research_agent(state: AgentState) -> AgentState:
    """Research specialist agent node."""
    try:
        chain = RESEARCH_PROMPT | research_llm
        response = chain.invoke({
            "task": state["task"],
            "correction_notes": state.get("correction_notes") or "None"
        })
        log_entry = f"[RESEARCH AGENT] Successfully processed research task."
        return {
            **state,
            "result": response.content,
            "error": None,
            "messages": state.get("messages", []) + [log_entry],
        }
    except Exception as e:
        error_msg = f"Research Agent Error: {str(e)}"
        return {
            **state,
            "error": error_msg,
            "messages": state.get("messages", []) + [f"[RESEARCH AGENT] {error_msg}"],
        }
