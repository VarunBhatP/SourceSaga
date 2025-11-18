"""
Agent: Generate technical solution plans using Cerebras Llama 3.3 70B.
"""
from typing import Dict
from graph.state import AgentState
from utils.cerebras_client import query_cerebras


def suggest_solution_agent(state: AgentState) -> Dict:
    """
    Generate step-by-step technical plans using Llama 3.3 70B.
    This is Cerebras's most powerful available model.
    """
    print("🧠 Agent: Generating solution plans...")
    
    analyses = state.get("analyses", [])
    
    for analysis in analyses:
        context = analysis["context"][:1500]
        
        prompt = f"""You are an expert software engineer analyzing a GitHub issue.

Analyze this issue and provide a detailed, step-by-step solution plan:

{context}

Provide a numbered action plan (6-10 steps) with:
- Specific files to modify
- Technical implementation details
- Code structure recommendations
- Testing approach

Be thorough and technically precise:"""
        
        print(f"  Generating plan for: {analysis['issue_url'][:50]}...")
        
        solution_plan = query_cerebras(
            prompt, 
            max_tokens=800,
            temperature=0.6,
            model="llama-3.3-70b"  # ✅ Using available 70B model
        )
        
        if not solution_plan:
            solution_plan = "Unable to generate plan. AI service temporarily unavailable."
        
        analysis["solution_plan"] = solution_plan
    
    print("✅ Solution plans generated")
    
    return {
        "analyses": analyses,
        "current_step": "solutions_ready"
    }
