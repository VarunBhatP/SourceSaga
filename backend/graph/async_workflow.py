"""
Async wrapper for running agents sequentially.
"""
import asyncio
from typing import Dict, Any


async def run_issue_search_async(skills: list) -> Dict[str, Any]:
    """Run only issue search."""
    from agents.issue_finder import find_issues_agent
    
    state = {
        "skills": skills,
        "selected_issue_urls": [],
        "analyses": [],
        "user_choice": None,
        "report_downloads": [],
        "current_step": "start",
        "error": None
    }
    
    result = await asyncio.to_thread(find_issues_agent, state)
    return result


async def run_analysis_async(
    issue_urls: list,
    generate_reports: bool = False
) -> Dict[str, Any]:
    """
    Run full analysis pipeline using YOUR working agents.
    """
    from agents.issue_finder import find_issues_agent
    from agents.code_analyzer import analyze_code_agent
    from agents.solution_suggester import suggest_solution_agent
    from agents.prompt_generator import generate_prompt_agent
    from agents.report_drafter import draft_report_agent
    
    print(f"\n🚀 Starting analysis for {len(issue_urls)} issue(s)...")
    
    # Step 1: Get issue details for the URLs
    # We need to call issue finder first to populate found_issues
    print("📍 Step 1: Fetching issue metadata...")
    search_state = await asyncio.to_thread(
        find_issues_agent,
        {"skills": [], "selected_issue_urls": [], "analyses": [], "user_choice": None, "report_downloads": [], "current_step": "start", "error": None}
    )
    
    # Filter to only our selected URLs
    all_found = search_state.get("found_issues", [])
    found_issues = [issue for issue in all_found if issue["url"] in issue_urls]
    
    # If we couldn't find them, create basic entries
    if not found_issues:
        found_issues = [
            {
                "url": url,
                "api_url": url.replace("github.com", "api.github.com/repos").replace("/issues/", "/issues/"),
                "title": "Issue",
                "repo": url.split("github.com/")[-1].split("/issues/")[0] if "github.com" in url else "unknown",
                "labels": []
            }
            for url in issue_urls
        ]
    
    state = {
        "skills": [],
        "found_issues": found_issues,
        "selected_issue_urls": issue_urls,
        "analyses": [],
        "user_choice": "draft_report" if generate_reports else "end",
        "report_downloads": [],
        "current_step": "start",
        "error": None
    }
    
    try:
        # Step 2: Analyze code (YOUR agent)
        print("📍 Step 2: Analyzing issues...")
        state = await asyncio.to_thread(analyze_code_agent, state)
        
        if not state.get("analyses"):
            print("❌ No analyses generated")
            return state
        
        # Step 3: Generate solution plans (YOUR agent)
        print("📍 Step 3: Generating solution plans...")
        state = await asyncio.to_thread(suggest_solution_agent, state)
        
        # Step 4: Generate prompts (YOUR agent)
        print("📍 Step 4: Generating prompts...")
        state = await asyncio.to_thread(generate_prompt_agent, state)
        
        # Step 5: Draft reports if requested (YOUR agent)
        if generate_reports:
            print("📍 Step 5: Drafting GSOC proposals...")
            state = await asyncio.to_thread(draft_report_agent, state)
        
        print(f"✅ Analysis complete for {len(state.get('analyses', []))} issues!\n")
        return state
    
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        state["error"] = str(e)
        return state
