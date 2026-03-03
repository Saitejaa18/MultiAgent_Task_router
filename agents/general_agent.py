"""
General Agent — Handles conversational, general, or unclassified tasks.
Uses Groq Llama 3 70B for fast, high-quality general responses.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state.schema import AgentState

load_dotenv()


general_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.6,
)

GENERAL_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful, friendly, and knowledgeable AI assistant.
Handle general conversations, opinions, greetings, and any tasks that don't 
specifically require coding, research, or summarization expertise.
Be concise but thorough. Respond in a natural, conversational tone.

If given correction notes from a previous attempt, incorporate that feedback."""
    ),
    ("human", "Task: {task}\n\nCorrection Notes (if any): {correction_notes}")
])


def general_agent(state: AgentState) -> AgentState:
    """General purpose agent node."""
    try:
        chain = GENERAL_PROMPT | general_llm
        response = chain.invoke({
            "task": state["task"],
            "correction_notes": state.get("correction_notes") or "None"
        })
        log_entry = f"[GENERAL AGENT] Successfully processed general task."
        return {
            **state,
            "result": response.content,
            "error": None,
            "messages": state.get("messages", []) + [log_entry],
        }
    except Exception as e:
        error_msg = f"General Agent Error: {str(e)}"
        return {
            **state,
            "error": error_msg,
            "messages": state.get("messages", []) + [f"[GENERAL AGENT] {error_msg}"],
        }
