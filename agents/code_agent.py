"""
Code Agent -- Handles all programming-related tasks.
Uses Groq Llama 3 70B for fast, high-quality code generation.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from state.schema import AgentState

load_dotenv()


code_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

CODE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert software engineer and coding assistant. 
Your responsibilities:
- Write clean, well-commented, production-ready code
- Debug and fix errors with clear explanations
- Explain code concepts clearly
- Suggest best practices and optimizations

If given correction notes from a previous attempt, incorporate that feedback.
Always format code in proper markdown code blocks with language specified."""
    ),
    ("human", "Task: {task}\n\nCorrection Notes (if any): {correction_notes}")
])


def code_agent(state: AgentState) -> AgentState:
    """Code specialist agent node."""
    try:
        chain = CODE_PROMPT | code_llm
        response = chain.invoke({
            "task": state["task"],
            "correction_notes": state.get("correction_notes") or "None"
        })
        log_entry = f"[CODE AGENT] Successfully processed coding task."
        return {
            **state,
            "result": response.content,
            "error": None,
            "messages": state.get("messages", []) + [log_entry],
        }
    except Exception as e:
        error_msg = f"Code Agent Error: {str(e)}"
        return {
            **state,
            "error": error_msg,
            "messages": state.get("messages", []) + [f"[CODE AGENT] {error_msg}"],
        }
