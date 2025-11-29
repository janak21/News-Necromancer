"""
Simple in-memory variant storage for story continuation.

WARNING: This is in-memory storage and will be lost on Vercel serverless cold starts.
For production with persistent storage, consider:
- Vercel KV (Redis) - requires paid plan
- Upstash Redis - has free tier
- Supabase - has free tier
- MongoDB Atlas - has free tier

Current behavior on Vercel:
- Variants stored during a function execution are available for ~15 minutes
- After cold start, all variants are lost
- Story continuation may fail if variant not found
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Global in-memory store (will reset on serverless function cold start)
_variant_store: Dict[str, dict] = {}
_store_ttl = timedelta(hours=24)  # Variants expire after 24 hours


def store_variant(variant_id: str, variant_data: dict) -> None:
    """
    Store a variant for later retrieval
    
    Args:
        variant_id: Unique variant identifier
        variant_data: Variant data including original_item, haunted_summary, etc.
    """
    _variant_store[variant_id] = {
        "data": variant_data,
        "stored_at": datetime.now()
    }
    logger.debug(f"Stored variant {variant_id}")


def get_variant(variant_id: str) -> Optional[dict]:
    """
    Retrieve a variant by ID
    
    Args:
        variant_id: Unique variant identifier
        
    Returns:
        Variant data or None if not found/expired
    """
    if variant_id not in _variant_store:
        logger.warning(f"Variant {variant_id} not found in store")
        return None
    
    stored = _variant_store[variant_id]
    stored_at = stored["stored_at"]
    
    # Check if expired
    if datetime.now() - stored_at > _store_ttl:
        logger.info(f"Variant {variant_id} expired, removing")
        del _variant_store[variant_id]
        return None
    
    return stored["data"]


def cleanup_expired() -> int:
    """
    Remove expired variants from store
    
    Returns:
        Number of variants removed
    """
    now = datetime.now()
    expired_ids = [
        vid for vid, stored in _variant_store.items()
        if now - stored["stored_at"] > _store_ttl
    ]
    
    for vid in expired_ids:
        del _variant_store[vid]
    
    if expired_ids:
        logger.info(f"Cleaned up {len(expired_ids)} expired variants")
    
    return len(expired_ids)


def get_store_stats() -> dict:
    """
    Get statistics about the variant store
    
    Returns:
        Dictionary with store statistics
    """
    return {
        "total_variants": len(_variant_store),
        "ttl_hours": _store_ttl.total_seconds() / 3600
    }
