from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    """
    Shared state passed between all agents in the LangGraph pipeline.
    """
    task: str                        # Original user input
    task_type: str                   # Determined by Router: "code" | "research" | "summarize" | "general"
    result: str                      # Final agent output
    error: Optional[str]             # Error message if agent failed
    retry_count: int                 # Number of self-correction attempts
    messages: List[str]              # Conversation / trace log
    correction_notes: Optional[str]  # Feedback from self-correction agent
