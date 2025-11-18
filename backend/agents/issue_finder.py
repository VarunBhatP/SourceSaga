"""
Agent: Find relevant GitHub issues based on user skills.
"""
from typing import Dict
from graph.state import AgentState
from utils.github_client import search_good_first_issues


def find_issues_agent(state: AgentState) -> Dict:
    """
    Search GitHub for good first issues matching the user's skills.
    
    Args:
        state: Current agent state with 'skills'
        
    Returns:
        Updated state with 'found_issues' and 'current_step'
    """
    print("🔍 Agent: Finding issues on GitHub...")
    
    skills = state.get("skills", [])
    
    if not skills:
        return {
            "error": "No skills provided",
            "current_step": "error"
        }
    
    issues = search_good_first_issues(skills, max_results=15)
    
    print(f"✅ Found {len(issues)} issues")
    
    return {
        "found_issues": issues,
        "current_step": "issues_found"
    }
