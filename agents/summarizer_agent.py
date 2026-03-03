"""
Summarizer Agent -- Condenses, extracts key points, and summarizes content.
Uses Groq Llama 3 70B for fast, concise structured summaries.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state.schema import AgentState

load_dotenv()


summarizer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert summarization specialist.
Your responsibilities:
- Extract the most important key points from any content
- Produce concise, well-structured summaries
- Use bullet points, TL;DR sections, and headers where helpful
- Preserve critical details while eliminating fluff
- Adapt the output length to the complexity of the content

If given correction notes from a previous attempt, incorporate that feedback.
Always start with a TL;DR line, then provide structured detail."""
    ),
    ("human", "Summarize this: {task}\n\nCorrection Notes (if any): {correction_notes}")
])


def summarizer_agent(state: AgentState) -> AgentState:
    """Summarizer specialist agent node."""
    try:
        chain = SUMMARIZE_PROMPT | summarizer_llm
        response = chain.invoke({
            "task": state["task"],
            "correction_notes": state.get("correction_notes") or "None"
        })
        log_entry = f"[SUMMARIZER AGENT] Successfully processed summarization task."
        return {
            **state,
            "result": response.content,
            "error": None,
            "messages": state.get("messages", []) + [log_entry],
        }
    except Exception as e:
        error_msg = f"Summarizer Agent Error: {str(e)}"
        return {
            **state,
            "error": error_msg,
            "messages": state.get("messages", []) + [f"[SUMMARIZER AGENT] {error_msg}"],
        }
