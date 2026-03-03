"""
Self-Correction Agent — Reviews a failed or poor-quality agent output
and generates correction notes to guide the retry attempt.
Uses Groq Llama 3 70B for fast, strong reasoning.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state.schema import AgentState

load_dotenv()


MAX_RETRIES = 3

correction_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

CORRECTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a quality control and debugging specialist for AI agents.
Your role is to:
1. Analyze a failed or poor-quality agent response
2. Diagnose what went wrong
3. Provide clear, actionable correction notes

Be specific. These correction notes will be passed back to the agent for a retry attempt.
Format: provide a numbered list of corrections the agent should make."""
    ),
    (
        "human",
        """Original Task: {task}
Task Type: {task_type}
Previous Result: {result}
Error (if any): {error}

What corrections should the agent make on its next attempt?"""
    )
])


def correction_agent(state: AgentState) -> AgentState:
    """
    Self-correction node. Generates correction notes and increments retry count.
    """
    try:
        chain = CORRECTION_PROMPT | correction_llm
        response = chain.invoke({
            "task": state["task"],
            "task_type": state.get("task_type", "unknown"),
            "result": state.get("result", "No result produced"),
            "error": state.get("error", "No explicit error"),
        })
        correction_notes = response.content
        log_entry = f"[CORRECTION AGENT] Generated corrections (Attempt {state.get('retry_count', 0) + 1}/{MAX_RETRIES})"
        return {
            **state,
            "correction_notes": correction_notes,
            "retry_count": state.get("retry_count", 0) + 1,
            "error": None,  # Clear error so worker retries cleanly
            "messages": state.get("messages", []) + [log_entry],
        }
    except Exception as e:
        return {
            **state,
            "retry_count": state.get("retry_count", 0) + 1,
            "correction_notes": "Please retry the task with more care.",
            "messages": state.get("messages", []) + [f"[CORRECTION AGENT] Error: {str(e)}"],
        }


def should_correct(state: AgentState) -> str:
    """
    Conditional edge after each worker agent.
    - If there's an error AND retries remaining → route to correction agent
    - If max retries reached → proceed to END with whatever we have
    - If no error → proceed to END successfully
    """
    has_error = bool(state.get("error"))
    retry_count = state.get("retry_count", 0)

    if has_error and retry_count < MAX_RETRIES:
        return "correct"
    return "done"


def after_correction_route(state: AgentState) -> str:
    """
    After correction agent runs, route back to the appropriate worker.
    """
    return state.get("task_type", "general")
