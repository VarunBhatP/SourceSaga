"""
Build the complete LangGraph workflow.
"""
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.router import route_after_feedback
from agents.issue_finder import find_issues_agent
from agents.code_analyzer import analyze_code_agent
from agents.solution_suggester import suggest_solution_agent
from agents.prompt_generator import generate_prompt_agent
from agents.report_drafter import draft_report_agent


def build_workflow() -> StateGraph:
    """
    Construct the complete agentic workflow graph.
    
    Returns:
        Compiled LangGraph StateGraph
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add all agent nodes
    workflow.add_node("find_issues", find_issues_agent)
    workflow.add_node("analyze_code", analyze_code_agent)
    workflow.add_node("suggest_solutions", suggest_solution_agent)
    workflow.add_node("generate_prompts", generate_prompt_agent)
    workflow.add_node("draft_reports", draft_report_agent)
    
    # Define the flow
    workflow.set_entry_point("find_issues")
    
    # Linear flow for analysis
    workflow.add_edge("find_issues", "analyze_code")
    workflow.add_edge("analyze_code", "suggest_solutions")
    workflow.add_edge("suggest_solutions", "generate_prompts")
    
    # After prompts are ready, wait for user feedback (handled externally)
    # The router will be called when user submits feedback
    
    workflow.add_conditional_edges(
        "generate_prompts",
        route_after_feedback,
        {
            "draft_reports": "draft_reports",
            "find_more_issues": "find_issues",
            "end": END
        }
    )
    
    workflow.add_edge("draft_reports", END)
    
    return workflow.compile()


# For testing
if __name__ == "__main__":
    graph = build_workflow()
    print("✅ Workflow compiled successfully")
