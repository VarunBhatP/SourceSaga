"""
Agent: Draft GSOC-style proposals as .docx files.
"""
import os
import uuid
from typing import Dict
from docx import Document
from graph.state import AgentState
from utils.llm_client import query_llm

LLAMA_MODEL = "meta-llama/Llama-3-8b-chat-hf"
DOWNLOADS_DIR = "downloads"


def draft_report_agent(state: AgentState) -> Dict:
    """
    Generate formal project proposals and save as .docx files.
    
    Args:
        state: Current agent state with 'analyses'
        
    Returns:
        Updated state with 'report_downloads' containing download URLs
    """
    print("📝 Agent: Drafting proposals...")
    
    analyses = state.get("analyses", [])
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    downloads = []
    
    for analysis in analyses:
        context = analysis["context"]
        plan = analysis["solution_plan"]
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are writing a Google Summer of Code project proposal.<|eot_id|>

<|start_header_id|>user<|end_header_id|>
Write a formal, compelling GSOC proposal based on this issue.

**Structure:**
1. Project Title
2. Problem Statement
3. Proposed Solution & Technical Approach
4. Timeline & Deliverables
5. Benefits to the Organization

**Issue Context:**
{context}

**Technical Plan:**
{plan}

Write the complete proposal now.<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>"""
        
        print(f"  Drafting proposal for: {analysis['issue_url'][:50]}...")
        proposal_text = query_llm(LLAMA_MODEL, prompt, max_tokens=800)
        
        if not proposal_text:
            continue
        
        # Create .docx file
        doc = Document()
        doc.add_heading('GSOC Project Proposal', level=1)
        doc.add_paragraph(proposal_text)
        
        filename = f"proposal_{uuid.uuid4().hex[:8]}.docx"
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        doc.save(filepath)
        
        downloads.append({
            "issue_title": analysis["context"].split("\n")[0].replace("**Issue Title:** ", ""),
            "download_url": f"{base_url}/download/{filename}"
        })
    
    print(f"✅ {len(downloads)} proposals drafted")
    
    return {
        "report_downloads": downloads,
        "current_step": "reports_ready"
    }
