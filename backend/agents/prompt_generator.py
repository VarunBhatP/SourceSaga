"""
Agent: Generate optimized prompts using Cerebras Llama 3.1 8B.
8B model is perfect for shorter, structured outputs.
"""
from typing import Dict
from graph.state import AgentState
from utils.cerebras_client import query_cerebras


def generate_prompt_agent(state: AgentState) -> Dict:
    """
    Create 'golden prompts' using Llama 3.1 8B.
    Fast model optimized for structured, shorter outputs.
    """
    print("✨ Agent: Generating AI-ready prompts...")
    
    analyses = state.get("analyses", [])
    
    for analysis in analyses:
        context = analysis["context"][:900]
        plan = analysis["solution_plan"][:700]
        
        prompt = f"""You are an expert at writing prompts for AI coding assistants.

Create a detailed, comprehensive coding prompt:

**Issue Context:**
{context}

**Solution Plan:**
{plan}

Write a well-structured prompt that includes:
1. Clear problem description
2. Technical requirements
3. Expected code structure
4. Testing requirements

Write the complete prompt that a developer can paste into ChatGPT/Claude:"""
        
        print(f"  Creating prompt for: {analysis['issue_url'][:50]}...")
        
        generated_prompt = query_cerebras(
            prompt, 
            max_tokens=600, 
            temperature=0.6,
            model="llama3.1-8b"  # ✅ Fast for shorter outputs
        )
        
        if not generated_prompt:
            generated_prompt = f"""Generate code to solve this GitHub issue:

{context[:300]}

Follow this technical approach:
{plan[:300]}

Provide complete, production-ready code with documentation."""
        
        analysis["generated_prompt"] = generated_prompt
    
    print("✅ Prompts generated")
    
    return {
        "analyses": analyses,
        "current_step": "prompts_ready"
    }
