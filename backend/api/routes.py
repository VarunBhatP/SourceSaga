"""
FastAPI routes for SourceSage API.
"""
import os
from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from api.models import (
    SearchIssuesRequest, SearchIssuesResponse,
    AnalyzeIssuesRequest, AnalyzeIssuesResponse,
    GitHubIssue, IssueAnalysis, ErrorResponse,
    ProgressUpdate, HealthResponse
)
from graph.async_workflow import run_issue_search_async, run_analysis_async
from database.cache import cache_github_search, get_cached_search, cache_analysis, get_cached_analysis

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        services={
            "github": "✅" if os.getenv("GITHUB_TOKEN") else "❌",
            "cerebras": "✅" if os.getenv("CEREBRAS_API_KEY") else "❌",
            "mongodb": "✅" if os.getenv("MONGODB_URL") else "⚠️ optional"
        }
    )


@router.post("/search-issues", response_model=SearchIssuesResponse)
async def search_issues(request: SearchIssuesRequest):
    """
    Search for GitHub 'good first issues' based on skills.
    
    Returns cached results if available.
    """
    try:
        # Check cache first
        cached = await get_cached_search(request.skills)
        if cached:
            return SearchIssuesResponse(
                success=True,
                issues=[GitHubIssue(**issue) for issue in cached[:request.max_results]],
                total_found=len(cached),
                message="✅ Retrieved from cache"
            )
        
        # Run workflow to find issues
        result = await run_issue_search_async(request.skills)
        
        found_issues = result.get("found_issues", [])
        
        if not found_issues:
            return SearchIssuesResponse(
                success=True,
                issues=[],
                total_found=0,
                message="No issues found for the given skills"
            )
        
        # Cache results
        await cache_github_search(request.skills, found_issues)
        
        return SearchIssuesResponse(
            success=True,
            issues=[GitHubIssue(**issue) for issue in found_issues[:request.max_results]],
            total_found=len(found_issues),
            message="✅ Search successful"
        )
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalyzeIssuesResponse)
async def analyze_issues(request: AnalyzeIssuesRequest):
    """Analyze selected issues and optionally generate GSOC proposals."""
    try:
        print(f"\n{'='*60}")
        print(f"📥 Analyze request:")
        print(f"   URLs: {request.issue_urls}")
        print(f"   Generate reports: {request.generate_reports}")
        print(f"{'='*60}\n")
        
        # Check cache for each issue
        cached_analyses = []
        uncached_urls = []
        
        for url in request.issue_urls:
            cached = await get_cached_analysis(url)
            if cached:
                print(f"✅ Using cached analysis for: {url}")
                cached_analyses.append(cached)
            else:
                uncached_urls.append(url)
        
        # Analyze uncached issues
        report_downloads = []
        
        if uncached_urls:
            print(f"🔄 Analyzing {len(uncached_urls)} new issue(s)...")
            
            result = await run_analysis_async(
                issue_urls=uncached_urls,
                generate_reports=request.generate_reports
            )
            
            if result.get("error"):
                raise Exception(result["error"])
            
            # Cache new analyses
            for analysis in result.get("analyses", []):
                await cache_analysis(analysis["issue_url"], analysis)
            
            new_analyses = result.get("analyses", [])
            report_downloads = result.get("report_downloads", [])  # ✅ Get reports from result
            
            all_analyses = cached_analyses + new_analyses
        else:
            # All from cache
            all_analyses = cached_analyses
            
            # If reports requested but we have cached data, we need to generate reports
            if request.generate_reports and cached_analyses:
                print("📝 Generating reports for cached analyses...")
                
                # Import the report drafter
                from agents.report_drafter import draft_report_agent
                import asyncio
                
                # Create state with cached analyses
                report_state = {
                    "analyses": cached_analyses,
                    "report_downloads": []
                }
                
                # Generate reports
                result = await asyncio.to_thread(draft_report_agent, report_state)
                report_downloads = result.get("report_downloads", [])
        
        print(f"\n{'='*60}")
        print(f"✅ Response: {len(all_analyses)} analyses, {len(report_downloads)} reports")
        print(f"{'='*60}\n")
        
        return AnalyzeIssuesResponse(
            success=True,
            analyses=[IssueAnalysis(**analysis) for analysis in all_analyses],
            report_downloads=report_downloads,
            message=f"✅ Analyzed {len(all_analyses)} issues"
        )
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ Error: {e}")
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/download/{filename}")
async def download_proposal(filename: str):
    """Download a generated GSOC proposal document."""
    file_path = os.path.join("downloads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# WebSocket for real-time progress
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time progress updates."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Add more WebSocket handling as needed
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
