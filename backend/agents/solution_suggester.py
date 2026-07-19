"""
Agent: Generate technical solution plans using a local free explainer.
"""
from typing import Dict
from graph.state import AgentState
from utils.free_explainer import generate_solution_plan


def suggest_solution_agent(state: AgentState) -> Dict:
    """
    Generate step-by-step technical plans without any external API.
    """
    print("🧠 Agent: Generating solution plans...")
    
    analyses = state.get("analyses", [])
    
    for analysis in analyses:
        context = analysis["context"][:1500]
        
        print(f"  Generating plan for: {analysis['issue_url'][:50]}...")
        solution_plan = generate_solution_plan(context, analysis["issue_url"])
        
        analysis["solution_plan"] = solution_plan
    
    print("✅ Solution plans generated")
    
    return {
        "analyses": analyses,
        "current_step": "solutions_ready"
    }
