"""
Test the LangGraph workflow without FastAPI.
"""
import os
from dotenv import load_dotenv
from graph.workflow import build_workflow

# Load environment variables
load_dotenv()

def main():
    """Run a test of the complete workflow."""
    
    print("=" * 60)
    print("🚀 SourceSage - Agent Workflow Test")
    print("=" * 60)
    
    # Build the graph
    graph = build_workflow()
    
    # Initial state
    initial_state = {
        "skills": ["node.js", "machine learning", "data analysis"],
        "selected_issue_urls": [],
        "analyses": [],
        "user_choice": None,
        "report_downloads": [],
        "current_step": "start",
        "error": None
    }
    
    # Step 1: Find issues
    print("\n📍 Step 1: Finding issues...")
    result = graph.invoke(initial_state)
    
    found_issues = result.get("found_issues", [])
    print(f"\nFound {len(found_issues)} issues:")
    for i, issue in enumerate(found_issues[:5], 1):
        print(f"  {i}. {issue['title'][:60]}...")
        print(f"     URL: {issue['url']}")
    
    # Simulate user selection
    if found_issues:
        selected = [found_issues[0]["url"]]  # Select first issue
        result["selected_issue_urls"] = selected
        
        # Step 2: Analyze
        print("\n📍 Step 2: Analyzing issue...")
        result = graph.invoke(result)
        
        print("\n✅ Analysis complete!")
        for analysis in result.get("analyses", []):
            print(f"\n📊 Solution Plan:")
            print(analysis.get("solution_plan", "")[:300] + "...")
            
            print(f"\n✨ Generated Prompt:")
            print(analysis.get("generated_prompt", "")[:300] + "...")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")


if __name__ == "__main__":
    main()
