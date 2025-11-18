"""
Agent: Generate optimized prompts for code generation LLMs.
"""
from typing import Dict
from graph.state import AgentState
from utils.llm_client import query_llm

LLAMA_MODEL = "meta-llama/Llama-3-8b-chat-hf"


def generate_prompt_agent(state: AgentState) -> Dict:
    """
    Create 'golden prompts' that users can feed to coding LLMs.
    
    Args:
        state: Current agent state with 'analyses' containing solution plans
        
    Returns:
        Updated state with generated prompts added to analyses
    """
    print("✨ Agent: Generating AI-ready prompts...")
    
    analyses = state.get("analyses", [])
    
    for analysis in analyses:
        context = analysis["context"]
        plan = analysis["solution_plan"]
        
        meta_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert prompt engineer for software development.<|eot_id|>

<|start_header_id|>user<|end_header_id|>
Create a single, comprehensive prompt for a code-generation AI (like Code Llama or GitHub Copilot). This prompt should allow the AI to write the complete implementation code.

Include:
1. Full technical context
2. The step-by-step plan
3. Clear instructions on what to generate

**Issue Context:**
{context}

**Solution Plan:**
{plan}

Generate the optimized prompt now.<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>"""
        
        print(f"  Creating prompt for: {analysis['issue_url'][:50]}...")
        generated_prompt = query_llm(LLAMA_MODEL, meta_prompt, max_tokens=700)
        
        analysis["generated_prompt"] = generated_prompt or "Error generating prompt"
    
    print("✅ Prompts generated")
    
    return {
        "analyses": analyses,
        "current_step": "prompts_ready"
    }
