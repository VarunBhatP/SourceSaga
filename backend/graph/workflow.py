"""
LangGraph workflow definition - Simplified.
"""
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.issue_finder import find_issues_agent
from agents.code_analyzer import analyze_code_agent
from agents.solution_suggester import suggest_solution_agent
from agents.prompt_generator import generate_prompt_agent
from agents.report_drafter import draft_report_agent


def build_workflow() -> StateGraph:
    """
    Build the complete LangGraph workflow.
    
    Simple linear flow:
    find_issues → analyze_code → suggest_solutions → generate_prompts → (conditional) draft_reports
    """
    
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("find_issues", find_issues_agent)
    workflow.add_node("analyze_code", analyze_code_agent)
    workflow.add_node("suggest_solutions", suggest_solution_agent)
    workflow.add_node("generate_prompts", generate_prompt_agent)
    workflow.add_node("draft_reports", draft_report_agent)
    
    # Set entry point
    workflow.set_entry_point("find_issues")
    
    # Linear edges
    workflow.add_edge("find_issues", "analyze_code")
    workflow.add_edge("analyze_code", "suggest_solutions")
    workflow.add_edge("suggest_solutions", "generate_prompts")
    
    # Conditional: generate reports or not
    def should_draft_reports(state: AgentState) -> str:
        """Check if we should draft reports."""
        user_choice = state.get("user_choice", "end")
        
        if user_choice == "draft_report":
            print("🔀 Drafting reports...")
            return "draft_reports"
        else:
            print("🔀 Skipping reports, ending...")
            return "end"
    
    workflow.add_conditional_edges(
        "generate_prompts",
        should_draft_reports,
        {
            "draft_reports": "draft_reports",
            "end": END
        }
    )
    
    workflow.add_edge("draft_reports", END)
    
    return workflow.compile()
