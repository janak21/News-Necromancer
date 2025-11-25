"""
Generation queue manager for handling concurrent narration requests.
"""

import asyncio
from asyncio import Queue, PriorityQueue
from enum import IntEnum
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class Priority(IntEnum):
    """Priority levels for narration generation requests."""
    HIGH = 1    # Currently visible content
    NORMAL = 2  # Off-screen content
    LOW = 3     # Background prefetch


@dataclass(order=True)
class QueuedRequest:
    """Represents a queued narration request."""
    priority: Priority = field(compare=True)
    created_at: datetime = field(compare=True)
    request_id: str = field(compare=False)
    request: Any = field(compare=False)  # NarrationRequest type


class GenerationQueueManager:
    """Manages concurrent narration generation requests with prioritization."""
    
    def __init__(self, max_concurrent: int = 3):
        """
        Initialize the generation queue manager.
        
        Args:
            max_concurrent: Maximum number of concurrent TTS API calls
        """
        self.max_concurrent = max_concurrent
        self.queue: PriorityQueue = PriorityQueue()
        self.active_requests: Dict[str, asyncio.Task] = {}
        self.request_status: Dict[str, Dict[str, Any]] = {}
        self.queued_items: Dict[str, QueuedRequest] = {}
        self._processing = False
        self._process_task: Optional[asyncio.Task] = None
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def enqueue(
        self, 
        request: Any,  # NarrationRequest type
        priority: Priority = Priority.NORMAL,
        generation_callback: Optional[Callable] = None
    ) -> str:
        """
        Add request to generation queue.
        
        Args:
            request: Narration generation request
            priority: Priority level for the request
            generation_callback: Optional async callback function to execute for generation
            
        Returns:
            Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        queued_request = QueuedRequest(
            priority=priority,
            created_at=created_at,
            request_id=request_id,
            request=request
        )
        
        # Store in queued items for position tracking
        self.queued_items[request_id] = queued_request
        
        # Initialize status
        self.request_status[request_id] = {
            "status": "queued",
            "progress": 0,
            "created_at": created_at,
            "priority": priority,
            "callback": generation_callback,
            "error": None,
            "result": None
        }
        
        # Add to priority queue
        await self.queue.put(queued_request)
        
        logger.info(f"Enqueued request {request_id} with priority {priority.name}")
        
        # Start processing if not already running
        if not self._processing:
            self._process_task = asyncio.create_task(self.process_queue())
        
        return request_id
    
    async def process_queue(self):
        """Process queued requests with concurrency limit."""
        if self._processing:
            return
        
        self._processing = True
        logger.info("Starting queue processing")
        
        try:
            while not self.queue.empty() or self.active_requests:
                # Process items from queue up to max_concurrent limit
                while len(self.active_requests) < self.max_concurrent and not self.queue.empty():
                    try:
                        queued_request = await asyncio.wait_for(
                            self.queue.get(), 
                            timeout=0.1
                        )
                        
                        request_id = queued_request.request_id
                        
                        # Check if request was cancelled while in queue
                        if request_id not in self.request_status:
                            continue
                        
                        if self.request_status[request_id]["status"] == "cancelled":
                            continue
                        
                        # Remove from queued items
                        self.queued_items.pop(request_id, None)
                        
                        # Update status to generating
                        self.request_status[request_id]["status"] = "generating"
                        self.request_status[request_id]["started_at"] = datetime.now()
                        
                        # Create task for processing
                        task = asyncio.create_task(
                            self._process_request(request_id, queued_request)
                        )
                        self.active_requests[request_id] = task
                        
                        logger.info(f"Started processing request {request_id}")
                        
                    except asyncio.TimeoutError:
                        break
                
                # Wait a bit before checking again
                if self.active_requests:
                    # Wait for at least one task to complete
                    done, pending = await asyncio.wait(
                        self.active_requests.values(),
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=0.5
                    )
                    
                    # Clean up completed tasks
                    for task in done:
                        for req_id, req_task in list(self.active_requests.items()):
                            if req_task == task:
                                del self.active_requests[req_id]
                                break
                else:
                    # No active requests, wait a bit
                    await asyncio.sleep(0.1)
                
                # Exit if queue is empty and no active requests
                if self.queue.empty() and not self.active_requests:
                    break
                    
        finally:
            self._processing = False
            logger.info("Queue processing stopped")
    
    async def _process_request(self, request_id: str, queued_request: QueuedRequest):
        """
        Process a single request with semaphore for concurrency control.
        
        Args:
            request_id: ID of the request
            queued_request: The queued request object
        """
        async with self._semaphore:
            try:
                # Get the callback function
                callback = self.request_status[request_id].get("callback")
                
                if callback:
                    # Execute the generation callback
                    result = await callback(queued_request.request)
                    
                    # Update status to completed
                    self.request_status[request_id]["status"] = "completed"
                    self.request_status[request_id]["progress"] = 100
                    self.request_status[request_id]["completed_at"] = datetime.now()
                    self.request_status[request_id]["result"] = result
                    
                    logger.info(f"Completed request {request_id}")
                else:
                    # No callback provided, just mark as completed
                    self.request_status[request_id]["status"] = "completed"
                    self.request_status[request_id]["progress"] = 100
                    self.request_status[request_id]["completed_at"] = datetime.now()
                    
            except asyncio.CancelledError:
                # Request was cancelled
                self.request_status[request_id]["status"] = "cancelled"
                self.request_status[request_id]["completed_at"] = datetime.now()
                logger.info(f"Request {request_id} was cancelled")
                raise
                
            except Exception as e:
                # Request failed
                self.request_status[request_id]["status"] = "failed"
                self.request_status[request_id]["error"] = str(e)
                self.request_status[request_id]["completed_at"] = datetime.now()
                logger.error(f"Request {request_id} failed: {str(e)}")
    
    async def cancel_request(self, request_id: str):
        """
        Cancel a queued or active request.
        
        Args:
            request_id: ID of the request to cancel
        """
        if request_id not in self.request_status:
            logger.warning(f"Request {request_id} not found")
            return
        
        current_status = self.request_status[request_id]["status"]
        
        if current_status in ["completed", "failed", "cancelled"]:
            logger.info(f"Request {request_id} already in terminal state: {current_status}")
            return
        
        # Update status to cancelled
        self.request_status[request_id]["status"] = "cancelled"
        self.request_status[request_id]["completed_at"] = datetime.now()
        
        # Remove from queued items if still in queue
        self.queued_items.pop(request_id, None)
        
        # Cancel active task if running
        if request_id in self.active_requests:
            task = self.active_requests[request_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.active_requests[request_id]
        
        logger.info(f"Cancelled request {request_id}")
    
    def get_status(self, request_id: str) -> Dict:
        """
        Get current status of a request.
        
        Args:
            request_id: ID of the request
            
        Returns:
            Dictionary containing request status information
        """
        if request_id not in self.request_status:
            return {
                "status": "not_found",
                "error": f"Request {request_id} not found"
            }
        
        status_info = self.request_status[request_id].copy()
        
        # Remove internal fields
        status_info.pop("callback", None)
        
        # Add queue position if still queued
        if status_info["status"] == "queued":
            status_info["queue_position"] = self.get_queue_position(request_id)
        
        return status_info
    
    def get_queue_position(self, request_id: str) -> int:
        """
        Get position in queue.
        
        Args:
            request_id: ID of the request
            
        Returns:
            Position in queue (0-indexed), or -1 if not in queue
        """
        if request_id not in self.queued_items:
            return -1
        
        # Get all queued items sorted by priority and creation time
        queued_list: List[QueuedRequest] = sorted(
            self.queued_items.values(),
            key=lambda x: (x.priority, x.created_at)
        )
        
        # Find position
        for position, queued_req in enumerate(queued_list):
            if queued_req.request_id == request_id:
                return position
        
        return -1
    
    async def shutdown(self):
        """Gracefully shutdown the queue manager."""
        logger.info("Shutting down queue manager")
        
        # Cancel all active requests
        for request_id in list(self.active_requests.keys()):
            await self.cancel_request(request_id)
        
        # Cancel processing task
        if self._process_task and not self._process_task.done():
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Queue manager shutdown complete")
