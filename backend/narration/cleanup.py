"""
Background cleanup tasks for narration system.

Handles periodic cleanup of:
- Expired cache entries (older than TTL)
- Abandoned generation requests (older than 1 hour in queued/generating state)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from backend.narration.audio_cache import AudioCacheManager
from backend.narration.queue_manager import GenerationQueueManager

logger = logging.getLogger(__name__)


class NarrationCleanupService:
    """
    Service for periodic cleanup of narration cache and queue.
    
    Runs cleanup tasks every 6 hours to:
    - Remove expired cache entries
    - Clean up abandoned generation requests
    """
    
    def __init__(
        self,
        cache_manager: AudioCacheManager,
        queue_manager: GenerationQueueManager,
        cleanup_interval_hours: int = 6,
        abandoned_request_timeout_hours: int = 1
    ):
        """
        Initialize the cleanup service.
        
        Args:
            cache_manager: Audio cache manager instance
            queue_manager: Generation queue manager instance
            cleanup_interval_hours: Hours between cleanup runs (default: 6)
            abandoned_request_timeout_hours: Hours before request is considered abandoned (default: 1)
        """
        self.cache_manager = cache_manager
        self.queue_manager = queue_manager
        self.cleanup_interval = timedelta(hours=cleanup_interval_hours)
        self.abandoned_timeout = timedelta(hours=abandoned_request_timeout_hours)
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the background cleanup service."""
        if self._running:
            logger.warning("Cleanup service is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info(
            f"Started cleanup service (interval: {self.cleanup_interval.total_seconds() / 3600}h, "
            f"abandoned timeout: {self.abandoned_timeout.total_seconds() / 3600}h)"
        )
    
    async def stop(self):
        """Stop the background cleanup service."""
        if not self._running:
            return
        
        self._running = False
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped cleanup service")
    
    async def _cleanup_loop(self):
        """Main cleanup loop that runs periodically."""
        try:
            while self._running:
                try:
                    # Run cleanup tasks
                    await self.run_cleanup()
                    
                    # Wait for next cleanup interval
                    await asyncio.sleep(self.cleanup_interval.total_seconds())
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {str(e)}", exc_info=True)
                    # Wait a bit before retrying
                    await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
    
    async def run_cleanup(self):
        """
        Run all cleanup tasks.
        
        This method can be called manually for immediate cleanup.
        """
        logger.info("Starting cleanup tasks")
        
        try:
            # Clean up expired cache entries
            await self._cleanup_expired_cache()
            
            # Clean up abandoned requests
            await self._cleanup_abandoned_requests()
            
            logger.info("Cleanup tasks completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
    
    async def _cleanup_expired_cache(self):
        """Remove cache entries older than TTL."""
        logger.info("Cleaning up expired cache entries")
        
        try:
            # Get initial cache size
            initial_count = len(self.cache_manager.cache_index)
            initial_size = self.cache_manager._get_total_cache_size()
            
            # Run cache cleanup
            await self.cache_manager.cleanup_expired()
            
            # Get final cache size
            final_count = len(self.cache_manager.cache_index)
            final_size = self.cache_manager._get_total_cache_size()
            
            # Calculate removed entries
            removed_count = initial_count - final_count
            freed_space_mb = (initial_size - final_size) / (1024 * 1024)
            
            if removed_count > 0:
                logger.info(
                    f"Removed {removed_count} expired cache entries, "
                    f"freed {freed_space_mb:.2f} MB"
                )
            else:
                logger.debug("No expired cache entries found")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {str(e)}", exc_info=True)
    
    async def _cleanup_abandoned_requests(self):
        """
        Clean up abandoned generation requests.
        
        Requests are considered abandoned if they've been in 'queued' or 'generating'
        state for longer than the abandoned_timeout.
        """
        logger.info("Cleaning up abandoned requests")
        
        try:
            now = datetime.now()
            abandoned_requests = []
            
            # Find abandoned requests
            for request_id, status_info in self.queue_manager.request_status.items():
                status = status_info.get("status")
                
                # Only check queued or generating requests
                if status not in ["queued", "generating"]:
                    continue
                
                # Check age of request
                created_at = status_info.get("created_at")
                if not created_at:
                    continue
                
                age = now - created_at
                
                if age > self.abandoned_timeout:
                    abandoned_requests.append(request_id)
            
            # Cancel abandoned requests
            for request_id in abandoned_requests:
                logger.warning(
                    f"Cancelling abandoned request {request_id} "
                    f"(age: {age.total_seconds() / 3600:.2f}h)"
                )
                await self.queue_manager.cancel_request(request_id)
            
            if abandoned_requests:
                logger.info(f"Cancelled {len(abandoned_requests)} abandoned requests")
            else:
                logger.debug("No abandoned requests found")
                
        except Exception as e:
            logger.error(f"Error cleaning up abandoned requests: {str(e)}", exc_info=True)
    
    async def get_cleanup_stats(self) -> dict:
        """
        Get statistics about the cleanup service.
        
        Returns:
            Dictionary containing cleanup statistics
        """
        cache_size_mb = self.cache_manager._get_total_cache_size() / (1024 * 1024)
        cache_count = len(self.cache_manager.cache_index)
        
        # Count requests by status
        status_counts = {}
        for status_info in self.queue_manager.request_status.values():
            status = status_info.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "running": self._running,
            "cleanup_interval_hours": self.cleanup_interval.total_seconds() / 3600,
            "abandoned_timeout_hours": self.abandoned_timeout.total_seconds() / 3600,
            "cache": {
                "entry_count": cache_count,
                "total_size_mb": round(cache_size_mb, 2),
                "max_size_mb": self.cache_manager.max_size_bytes / (1024 * 1024),
                "ttl_days": self.cache_manager.ttl.days
            },
            "requests": {
                "total": len(self.queue_manager.request_status),
                "by_status": status_counts,
                "active": len(self.queue_manager.active_requests),
                "queued": len(self.queue_manager.queued_items)
            }
        }
