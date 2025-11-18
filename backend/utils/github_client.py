"""
GitHub API client for fetching issues and repository information.
"""
import os
import requests
from typing import List, Dict

GITHUB_API_URL = "https://api.github.com"


def _get_headers():
    """Get GitHub API headers with authentication."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables")
    
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }


def search_good_first_issues(skills: List[str], max_results: int = 15) -> List[Dict]:
    """
    Search GitHub for 'good first issue' labeled issues matching the given skills.
    
    Args:
        skills: List of programming languages/frameworks
        max_results: Maximum number of issues to return
        
    Returns:
        List of issue dictionaries with url, title, repo, and labels
    """
    try:
        headers = _get_headers()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return []
    
    # Map frameworks to their underlying languages
    language_map = {
        "fastapi": "python",
        "django": "python",
        "flask": "python",
        "react": "javascript",
        "vue": "javascript",
        "angular": "typescript",
        "express": "javascript",
        "nextjs": "javascript",
    }
    
    # Convert skills to proper GitHub languages
    languages = set()
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in language_map:
            languages.add(language_map[skill_lower])
        else:
            languages.add(skill_lower)
    
    # Build search query with proper languages
    if languages:
        language_query = " ".join([f"language:{lang}" for lang in languages])
        query = f'is:issue is:open label:"good first issue" {language_query}'
    else:
        query = 'is:issue is:open label:"good first issue"'
    
    params = {
        "q": query,
        "sort": "created",
        "order": "desc",
        "per_page": max_results
    }
    
    print(f"🔍 Searching GitHub with query: {query}")
    
    try:
        response = requests.get(
            f"{GITHUB_API_URL}/search/issues",
            headers=headers,
            params=params,
            timeout=10
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Authentication failed! Check your GitHub token.")
            return []
        
        if response.status_code == 403:
            print("❌ Rate limit exceeded or insufficient permissions!")
            print(f"Rate limit: {response.headers.get('X-RateLimit-Remaining', 'unknown')}/{response.headers.get('X-RateLimit-Limit', 'unknown')}")
            return []
        
        response.raise_for_status()
        
        data = response.json()
        total_count = data.get("total_count", 0)
        print(f"✅ GitHub returned {total_count} total issues")
        
        issues = []
        
        for item in data.get("items", []):
            issues.append({
                "url": item["html_url"],
                "api_url": item["url"],
                "title": item["title"],
                "repo": item["repository_url"].split("/")[-1],
                "labels": [label["name"] for label in item.get("labels", [])]
            })
        
        print(f"✅ Processed {len(issues)} issues")
        return issues
    
    except Exception as e:
        print(f"❌ Error fetching issues: {e}")
        return []



def get_issue_details(issue_api_url: str) -> Dict:
    """
    Fetch detailed information about a specific issue.
    
    Args:
        issue_api_url: The API URL for the issue
        
    Returns:
        Dictionary with issue body, comments, and related file info
    """
    try:
        headers = _get_headers()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return {"title": "", "body": "", "comments": []}
    
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
        print(f"❌ Error fetching issue details: {e}")
        return {"title": "", "body": "", "comments": []}
