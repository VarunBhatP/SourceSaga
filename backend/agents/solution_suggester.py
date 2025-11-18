"""
Agent: Generate technical solution plans using Code Llama.
"""
from typing import Dict
from graph.state import AgentState
from utils.llm_client import query_llm

CODE_LLAMA_MODEL = "codellama/CodeLlama-34b-Instruct-hf"


def suggest_solution_agent(state: AgentState) -> Dict:
    """
    Generate step-by-step technical plans for each analyzed issue.
    
    Args:
        state: Current agent state with 'analyses'
        
    Returns:
        Updated state with solution plans added to analyses
    """
    print("🧠 Agent: Generating solution plans...")
    
    analyses = state.get("analyses", [])
    
    for analysis in analyses:
        context = analysis["context"]
        
        prompt = f"""<s>[INST] You are an expert software developer helping someone contribute to open source.

Analyze the following GitHub issue and provide a clear, step-by-step technical plan to solve it.

{context}

Provide a numbered, actionable plan. Be specific about what files might need to be changed and what logic to implement. [/INST]"""
        
        print(f"  Generating plan for: {analysis['issue_url'][:50]}...")
        solution_plan = query_llm(CODE_LLAMA_MODEL, prompt, max_tokens=600)
        
        analysis["solution_plan"] = solution_plan or "Error generating plan"
    
    print("✅ Solution plans generated")
    
    return {
        "analyses": analyses,
        "current_step": "solutions_ready"
    }
