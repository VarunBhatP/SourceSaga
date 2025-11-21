"""
Agent: Draft GSOC proposals using Cerebras Llama 3.3 70B.
Llama 3.3 70B provides the best quality for formal writing.
"""
import os
import uuid
from typing import Dict
from docx import Document
from graph.state import AgentState
from utils.cerebras_client import query_cerebras

DOWNLOADS_DIR = "downloads"


def draft_report_agent(state: AgentState) -> Dict:
    """
    Generate formal proposals using Llama 3.3 70B.
    Largest model for highest quality formal writing.
    """
    print("📝 Agent: Drafting proposals...")
    
    analyses = state.get("analyses", [])
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    downloads = []
    
    for analysis in analyses:
        context = analysis["context"][:1000]
        plan = analysis["solution_plan"][:800]
        
        prompt = f"""Write a formal, professional Google Summer of Code (GSOC) project proposal.

**Issue Context:**
{context}

**Technical Plan:**
{plan}

Write a complete, well-structured proposal with:

1. **Project Title** (creative and descriptive)
2. **Abstract** (2-3 sentences)
3. **Problem Statement** (what needs fixing)
4. **Proposed Solution** (detailed technical approach)
5. **Implementation Plan** (12-week timeline with milestones)
6. **Deliverables** (concrete outputs)
7. **Benefits** (project impact)
8. **About Me** (placeholder for contributor background)

Use professional, formal tone. Be thorough and persuasive:"""
        
        print(f"  Drafting proposal for: {analysis['issue_url'][:50]}...")
        
        proposal_text = query_cerebras(
            prompt, 
            max_tokens=1200, 
            temperature=0.6,
            model="llama-3.3-70b"  # ✅ Best quality for formal writing
        )
        
        if not proposal_text:
            proposal_text = f"""# Google Summer of Code Project Proposal

## Abstract
This proposal addresses a critical feature request in the project.

## Problem Statement
{context[:400]}

## Proposed Technical Approach
{plan[:400]}

## Implementation Timeline
**Weeks 1-4:** Foundation and setup
**Weeks 5-8:** Core implementation
**Weeks 9-11:** Testing and refinement
**Week 12:** Documentation and review

## Deliverables
- Fully functional implementation
- Comprehensive test suite
- Complete documentation

## Benefits
This contribution will significantly enhance the project's functionality and user experience."""
        
        # Create .docx file
        doc = Document()
        doc.add_heading('Google Summer of Code Project Proposal', level=1)
        
        # Parse and format the proposal
        for line in proposal_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('###'):
                doc.add_heading(line.replace('#', '').strip(), level=3)
            elif line.startswith('##'):
                doc.add_heading(line.replace('#', '').strip(), level=2)
            elif line.startswith('#'):
                doc.add_heading(line.replace('#', '').strip(), level=1)
            elif line.startswith('**') and line.endswith('**'):
                doc.add_heading(line.replace('**', ''), level=3)
            else:
                doc.add_paragraph(line)
        
        filename = f"proposal_{uuid.uuid4().hex[:8]}.docx"
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        doc.save(filepath)
        
        issue_title = analysis["context"].split("\n")[0].replace("**Issue Title:** ", "")
        downloads.append({
            "issue_title": issue_title[:60],
            "download_url": f"{base_url}/api/download/{filename}"
        })
    
    print(f"✅ {len(downloads)} proposals drafted")
    
    return {
        "analyses": analyses,  # ✅ Keep the analyses!
        "report_downloads": downloads,
        "current_step": "reports_ready"
    }

