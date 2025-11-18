"""
GitHub API client for fetching issues and repository information.
"""
import os
import requests
from typing import List, Dict

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com"

def search_good_first_issues(skills: List[str], max_results: int = 15) -> List[Dict]:
    """
    Search GitHub for 'good first issue' labeled issues matching the given skills.
    
    Args:
        skills: List of programming languages/frameworks
        max_results: Maximum number of issues to return
        
    Returns:
        List of issue dictionaries with url, title, repo, and labels
    """
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Build search query
    language_query = " OR ".join([f"language:{skill}" for skill in skills])
    query = f'is:issue is:open label:"good first issue" ({language_query})'
    
    params = {
        "q": query,
        "sort": "created",
        "order": "desc",
        "per_page": max_results
    }
    
    try:
        response = requests.get(
            f"{GITHUB_API_URL}/search/issues",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        issues = []
        
        for item in data.get("items", []):
            issues.append({
                "url": item["html_url"],
                "api_url": item["url"],
                "title": item["title"],
                "repo": item["repository_url"].split("/")[-1],
                "labels": [label["name"] for label in item.get("labels", [])]
            })
        
        return issues
    
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []


def get_issue_details(issue_api_url: str) -> Dict:
    """
    Fetch detailed information about a specific issue.
    
    Args:
        issue_api_url: The API URL for the issue
        
    Returns:
        Dictionary with issue body, comments, and related file info
    """
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Get issue details
        response = requests.get(issue_api_url, headers=headers, timeout=10)
        response.raise_for_status()
        issue_data = response.json()
        
        # Get comments
        comments_response = requests.get(
            issue_data["comments_url"],
            headers=headers,
            timeout=10
        )
        comments_data = comments_response.json() if comments_response.ok else []
        
        return {
            "title": issue_data["title"],
            "body": issue_data.get("body", ""),
            "comments": [c.get("body", "") for c in comments_data[:5]],  # First 5 comments
            "created_at": issue_data["created_at"],
            "state": issue_data["state"]
        }
    
    except Exception as e:
        print(f"Error fetching issue details: {e}")
        return {"title": "", "body": "", "comments": []}
