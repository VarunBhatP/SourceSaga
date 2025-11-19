"""
Conditional routing logic for LangGraph workflow.
"""
from graph.state import AgentState


def route_after_feedback(state: AgentState) -> str:
    """
    Route after generating prompts based on user choice.
    
    Options:
    - "draft_report": Generate GSOC proposal documents
    - "find_more": Search for more issues
    - "end": Finish workflow
    """
    user_choice = state.get("user_choice")
    
    print(f"🔀 Router: user_choice = {user_choice}")
    
    if user_choice == "draft_report":
        return "draft_reports"
    elif user_choice == "find_more":
        return "find_more_issues"
    else:
        # Default to end
        return "end"
