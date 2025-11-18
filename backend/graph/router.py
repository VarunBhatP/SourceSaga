"""
Conditional routing logic for the LangGraph workflow.
"""
from graph.state import AgentState
from typing import Literal


def route_after_feedback(
    state: AgentState
) -> Literal["draft_reports", "find_more_issues", "end"]:
    """
    Route the workflow based on user's feedback choice.
    
    Args:
        state: Current agent state with 'user_choice'
        
    Returns:
        The name of the next node to execute
    """
    choice = state.get("user_choice", "end")
    
    if choice == "draft_report":
        return "draft_reports"
    elif choice == "find_more":
        return "find_more_issues"
    else:
        return "end"
