"""
Integration layer for coordinating fetcher and remixer modules
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..models.data_models import (
    FeedItem, SpookyVariant, UserPreferences, ProcessingStats, 
    FetchResult, ProcessingResponse
)
from ..fetcher.concurrent_fetcher import ConcurrentFetcher
from ..remixer.spooky_remixer import SpookyRemixer

logger = logging.getLogger(__name__)


class SpookyIntegrationManager:
    """
    Manages integration between fetcher and remixer modules with enhanced coordination
    """
    
    def __init__(self, fetcher: ConcurrentFetcher, remixer: SpookyRemixer):
        self.fetcher = fetcher
        self.remixer = remixer
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = asyncio.Lock()
    
    async def process_feeds_integrated(
        self, 
        urls: List[str], 
        user_preferences: Optional[UserPreferences] = None,
        variant_count: int = 2,
        session_id: Optional[str] = None
    ) -> ProcessingResponse:
        """
        Process feeds with integrated fetcher and remixer coordination
        
        Args:
            urls: List of RSS feed URLs to process
            user_preferences: User preferences for personalization
            variant_count: Number of variants to generate per item
            session_id: Optional session ID for tracking
            
        Returns:
            ProcessingResponse with results and statistics
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        start_time = datetime.now()
        
        try:
            logger.info(f"🎃 Starting integrated processing session {session_id} for {len(urls)} feeds")
            
            # Initialize session tracking
            async with self.session_lock:
                self.active_sessions[session_id] = {
                    "start_time": start_time,
                    "status": "processing",
                    "urls": urls,
                    "user_preferences": user_preferences,
                    "variant_count": variant_count
                }
            
            # Phase 1: Concurrent feed fetching
            logger.info(f"👻 Phase 1: Fetching {len(urls)} feeds concurrently")
            fetch_results = await self.fetcher.fetch_feeds_concurrent(urls)
            
            # Collect all feed items
            all_items = []
            successful_fetches = 0
            failed_fetches = 0
            
            for result in fetch_results:
                if result.success:
                    all_items.extend(result.items)
                    successful_fetches += 1
                else:
                    failed_fetches += 1
                    logger.warning(f"⚠️ Failed to fetch {result.url}: {result.error}")
            
            logger.info(f"🕷️ Fetched {len(all_items)} items from {successful_fetches} feeds ({failed_fetches} failed)")
            
            # Phase 2: Batch processing with remixer
            logger.info(f"🎭 Phase 2: Generating spooky variants for {len(all_items)} items")
            
            # Process items in batches for better performance
            batch_size = 10
            all_variants = []
            
            for i in range(0, len(all_items), batch_size):
                batch = all_items[i:i + batch_size]
                logger.info(f"🧙‍♀️ Processing batch {i//batch_size + 1}/{(len(all_items) + batch_size - 1)//batch_size}")
                
                # Process batch concurrently
                batch_tasks = []
                for item in batch:
                    task = asyncio.create_task(
                        self._generate_variants_async(item, variant_count, user_preferences)
                    )
                    batch_tasks.append(task)
                
                # Wait for batch completion
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Collect successful results
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"💀 Error generating variants: {str(result)}")
                    else:
                        all_variants.extend(result)
            
            # Calculate final statistics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            stats = ProcessingStats(
                feeds_processed=successful_fetches,
                variants_generated=len(all_variants),
                processing_time=processing_time,
                error_count=failed_fetches,
                start_time=start_time,
                end_time=end_time
            )
            
            # Update session status
            async with self.session_lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id].update({
                        "status": "completed",
                        "end_time": end_time,
                        "stats": stats,
                        "variants": all_variants
                    })
            
            logger.info(f"✨ Completed session {session_id}: {len(all_variants)} variants in {processing_time:.2f}s")
            
            return ProcessingResponse(
                success=True,
                message=f"Successfully processed {successful_fetches} feeds and generated {len(all_variants)} spooky variants",
                processing_id=session_id,
                stats=stats,
                variants=all_variants
            )
            
        except Exception as e:
            logger.error(f"💀 Integration processing failed for session {session_id}: {str(e)}")
            
            # Update session with error
            async with self.session_lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id].update({
                        "status": "failed",
                        "error": str(e),
                        "end_time": datetime.now()
                    })
            
            return ProcessingResponse(
                success=False,
                message=f"Processing failed: {str(e)}",
                processing_id=session_id
            )
    
    async def _generate_variants_async(
        self, 
        item: FeedItem, 
        count: int, 
        preferences: Optional[UserPreferences]
    ) -> List[SpookyVariant]:
        """
        Generate variants asynchronously for a single feed item
        
        Args:
            item: Feed item to process
            count: Number of variants to generate
            preferences: User preferences for personalization
            
        Returns:
            List of generated spooky variants
        """
        try:
            # Run the synchronous remixer method in a thread pool
            loop = asyncio.get_event_loop()
            variants = await loop.run_in_executor(
                None, 
                self.remixer.generate_variants, 
                item, 
                count, 
                preferences
            )
            return variants
        except Exception as e:
            logger.error(f"💀 Error generating variants for item '{item.title}': {str(e)}")
            return []
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a processing session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session status information or None if not found
        """
        async with self.session_lock:
            return self.active_sessions.get(session_id)
    
    async def cleanup_session(self, session_id: str) -> bool:
        """
        Clean up a completed session to free memory
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was found and cleaned up
        """
        async with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"🧹 Cleaned up session {session_id}")
                return True
            return False
    
    async def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all active sessions
        
        Returns:
            Dictionary of active sessions
        """
        async with self.session_lock:
            # Return a copy to avoid concurrent modification issues
            return {
                session_id: {
                    "session_id": session_id,
                    "status": session_data["status"],
                    "start_time": session_data["start_time"].isoformat(),
                    "urls_count": len(session_data["urls"]),
                    "variant_count": session_data["variant_count"]
                }
                for session_id, session_data in self.active_sessions.items()
            }
    
    def get_integration_health(self) -> Dict[str, Any]:
        """
        Get health status of the integration layer
        
        Returns:
            Integration health information
        """
        try:
            # Check fetcher health
            fetcher_healthy = hasattr(self.fetcher, 'fetch_feeds_concurrent')
            
            # Check remixer health  
            remixer_healthy = hasattr(self.remixer, 'generate_variants')
            
            # Count active sessions
            active_count = len(self.active_sessions)
            
            return {
                "status": "healthy" if (fetcher_healthy and remixer_healthy) else "unhealthy",
                "components": {
                    "fetcher": "healthy" if fetcher_healthy else "unhealthy",
                    "remixer": "healthy" if remixer_healthy else "unhealthy",
                    "session_manager": "healthy"
                },
                "active_sessions": active_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"💀 Integration health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }