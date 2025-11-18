"""
Agent: Analyze the context of a selected GitHub issue.
"""
from typing import Dict
from graph.state import AgentState
from utils.github_client import get_issue_details


def analyze_code_agent(state: AgentState) -> Dict:
    """
    Fetch and compile detailed context for each selected issue.
    
    Args:
        state: Current agent state with 'selected_issue_urls' and 'found_issues'
        
    Returns:
        Updated state with issue contexts ready for analysis
    """
    print("📖 Agent: Analyzing selected issues...")
    
    selected_urls = state.get("selected_issue_urls", [])
    found_issues = state.get("found_issues", [])
    
    # Map URLs to API URLs
    url_to_api = {issue["url"]: issue["api_url"] for issue in found_issues}
    
    analyses = []
    
    for url in selected_urls:
        api_url = url_to_api.get(url)
        if not api_url:
            continue
        
        print(f"  Fetching details for: {url}")
        details = get_issue_details(api_url)
        
        # Compile context
        context = f"""
**Issue Title:** {details['title']}

**Description:**
{details['body']}

**Recent Comments:**
{chr(10).join(details['comments'][:3])}
"""
        
        analyses.append({
            "issue_url": url,
            "context": context.strip(),
            "solution_plan": "",  # Will be filled by next agent
            "generated_prompt": ""  # Will be filled later
        })
    
    print(f"✅ Analyzed {len(analyses)} issues")
    
    return {
        "analyses": analyses,
        "current_step": "analysis_complete"
    }
