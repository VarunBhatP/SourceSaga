"""
Cache operations for GitHub issues and analyses.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .connection import get_db


async def cache_github_search(
    skills: List[str],
    issues: List[Dict[str, Any]],
    ttl_hours: int = 24
) -> bool:
    """Cache GitHub search results."""
    try:
        db = await get_db()
        if db is None:  # ✅ Fixed: Check against None explicitly
            return False
        
        cache_key = "_".join(sorted(skills))
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        await db.issues_cache.update_one(
            {"cache_key": cache_key},
            {
                "$set": {
                    "skills": skills,
                    "issues": issues,
                    "cached_at": datetime.utcnow(),
                    "expires_at": expires_at
                }
            },
            upsert=True
        )
        
        return True
    
    except Exception as e:
        print(f"⚠️ Cache write failed: {e}")
        return False


async def get_cached_search(skills: List[str]) -> Optional[List[Dict[str, Any]]]:
    """Get cached GitHub search results."""
    try:
        db = await get_db()
        if db is None:  # ✅ Fixed
            return None
        
        cache_key = "_".join(sorted(skills))
        
        result = await db.issues_cache.find_one({
            "cache_key": cache_key,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if result:
            print(f"✅ Cache hit for: {skills}")
            return result.get("issues")
        
        return None
    
    except Exception as e:
        print(f"⚠️ Cache read failed: {e}")
        return None


async def cache_analysis(
    issue_url: str,
    analysis: Dict[str, Any],
    ttl_hours: int = 168
) -> bool:
    """Cache issue analysis."""
    try:
        db = await get_db()
        if db is None:  # ✅ Fixed
            return False
        
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        await db.analyses_cache.update_one(
            {"issue_url": issue_url},
            {
                "$set": {
                    "analysis": analysis,
                    "cached_at": datetime.utcnow(),
                    "expires_at": expires_at
                }
            },
            upsert=True
        )
        
        return True
    
    except Exception as e:
        print(f"⚠️ Analysis cache write failed: {e}")
        return False


async def get_cached_analysis(issue_url: str) -> Optional[Dict[str, Any]]:
    """Get cached analysis."""
    try:
        db = await get_db()
        if db is None:  # ✅ Fixed
            return None
        
        result = await db.analyses_cache.find_one({
            "issue_url": issue_url,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if result:
            print(f"✅ Analysis cache hit for: {issue_url}")
            return result.get("analysis")
        
        return None
    
    except Exception as e:
        print(f"⚠️ Analysis cache read failed: {e}")
        return None
