"""
Define the AgentState that will be passed between all agents in the graph.
This is the central data structure for your workflow.
"""
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """The state object that flows through the LangGraph workflow."""
    
    # User input
    skills: List[str]
    
    # Issue discovery
    found_issues: List[dict]  # List of {url, title, repo, labels}
    selected_issue_urls: List[str]  # Which issues user selected
    
    # Analysis results (one per selected issue)
    analyses: List[dict]  # Each: {issue_url, context, solution_plan, generated_prompt}
    
    # User feedback
    user_choice: Optional[str]  # "draft_report", "find_more", "end"
    
    # Final outputs
    report_downloads: List[dict]  # Each: {issue_title, download_url}
    
    # System state
    current_step: str  # For tracking workflow progress
    error: Optional[str]  # For error handling
