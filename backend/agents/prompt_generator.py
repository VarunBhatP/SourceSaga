"""
Agent: Generate optimized prompts using a local free explainer.
"""
from typing import Dict
from graph.state import AgentState
from utils.free_explainer import generate_coding_prompt


def generate_prompt_agent(state: AgentState) -> Dict:
    """
    Create coding prompts without any external API.
    """
    print("✨ Agent: Generating AI-ready prompts...")
    
    analyses = state.get("analyses", [])
    
    for analysis in analyses:
        context = analysis["context"][:900]
        plan = analysis["solution_plan"][:700]
        
        print(f"  Creating prompt for: {analysis['issue_url'][:50]}...")
        generated_prompt = generate_coding_prompt(
            context,
            plan,
            analysis["issue_url"],
        )
        
        analysis["generated_prompt"] = generated_prompt
    
    print("✅ Prompts generated")
    
    return {
        "analyses": analyses,
        "current_step": "prompts_ready"
    }
