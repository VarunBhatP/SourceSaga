"""
Pydantic models for request/response validation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============= Request Models =============

class SearchIssuesRequest(BaseModel):
    """Request to search for GitHub issues."""
    skills: List[str] = Field(..., min_items=1, max_items=10, description="Programming languages/frameworks")
    max_results: int = Field(15, ge=1, le=50, description="Maximum number of issues to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "skills": ["python", "fastapi"],
                "max_results": 15
            }
        }


class AnalyzeIssuesRequest(BaseModel):
    """Request to analyze selected issues."""
    issue_urls: List[str] = Field(..., min_items=1, max_items=5, description="GitHub issue URLs to analyze")
    generate_reports: bool = Field(False, description="Whether to generate GSOC proposals")
    
    class Config:
        json_schema_extra = {
            "example": {
                "issue_urls": [
                    "https://github.com/owner/repo/issues/123"
                ],
                "generate_reports": True
            }
        }


# ============= Response Models =============

class GitHubIssue(BaseModel):
    """Represents a GitHub issue."""
    url: str
    title: str
    repo: str
    labels: List[str] = []


class SearchIssuesResponse(BaseModel):
    """Response from issue search."""
    success: bool
    issues: List[GitHubIssue]
    total_found: int
    message: Optional[str] = None


class IssueAnalysis(BaseModel):
    """Analysis result for a single issue."""
    issue_url: str
    context: str
    solution_plan: str
    generated_prompt: str


class AnalyzeIssuesResponse(BaseModel):
    """Response from issue analysis."""
    success: bool
    analyses: List[IssueAnalysis]
    report_downloads: List[Dict[str, str]] = []
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ============= WebSocket Models =============

class ProgressUpdate(BaseModel):
    """Progress update for WebSocket."""
    stage: str  # "finding", "analyzing", "planning", "prompting", "reporting", "complete"
    message: str
    progress: int  # 0-100
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"
    services: Dict[str, str]
