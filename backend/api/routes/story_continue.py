"""
Story continuation API routes
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from ...remixer.spooky_remixer import SpookyRemixer
from ...models.data_models import StoryContinuation
from ...config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/story_continue", tags=["story_continue"])

# In-memory variant store (same as serverless)
_variant_store = {}


class StoryContinuationRequest(BaseModel):
    """Request model for story continuation"""
    variant_id: str = Field(..., description="ID of the variant to continue")
    content: str = Field(..., description="Original story content to continue")
    continuation_length: int = Field(500, ge=300, le=1000, description="Target length in characters")


class StoryContinuationResponse(BaseModel):
    """Response model for story continuation"""
    success: bool
    variant_id: str
    continuation: dict


@router.post("", response_model=StoryContinuationResponse)
async def continue_story(request: StoryContinuationRequest):
    """
    Continue a spooky story with more horror content
    
    Args:
        request: Story continuation request
        
    Returns:
        Continuation with extended narrative
    """
    try:
        settings = get_settings()
        
        # Check if variant exists in store
        if request.variant_id in _variant_store:
            stored_variant = _variant_store[request.variant_id]
            logger.info(f"Found variant {request.variant_id} in store")
            # Use stored content if no content provided
            if not request.content:
                request.content = stored_variant.get('haunted_summary', '')
        
        if not request.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Original story content is required"
            )
        
        # Initialize remixer
        remixer = SpookyRemixer(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            app_name=settings.openrouter_app_name,
            enable_caching=False
        )
        
        # Generate continuation using OpenRouter
        continuation_text = await generate_continuation_async(
            remixer,
            request.variant_id,
            request.content,
            request.continuation_length
        )
        
        return StoryContinuationResponse(
            success=True,
            variant_id=request.variant_id,
            continuation={
                "continued_narrative": continuation_text,
                "continuation_themes": ["supernatural", "horror", "mystery"],
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error continuing story: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to continue story: {str(e)}"
        )


async def generate_continuation_async(
    remixer: SpookyRemixer,
    variant_id: str,
    original_content: str,
    continuation_length: int
) -> str:
    """Generate story continuation using OpenRouter"""
    
    prompt = f"""Continue this horror story with more supernatural and terrifying details.

Original Story:
{original_content}

Continue the nightmare with:
1. Escalate the horror and supernatural elements
2. Add more disturbing details and atmosphere
3. Keep the same tone and style
4. Make it approximately {continuation_length} characters
5. End with a cliffhanger or revelation

Return ONLY the continuation text, no JSON, no formatting.
"""
    
    try:
        response = remixer.client.chat.completions.create(
            model=remixer.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=min(continuation_length // 2, 500),
            temperature=0.8
        )
        
        continuation_text = response.choices[0].message.content.strip()
        logger.info(f"Generated continuation for variant {variant_id}: {len(continuation_text)} chars")
        
        return continuation_text
        
    except Exception as e:
        logger.error(f"OpenRouter API error: {str(e)}")
        # Fallback continuation
        return f"The darkness deepens as the supernatural forces grow stronger. What began as {original_content[:50]}... now spirals into absolute terror. Ancient entities stir in the shadows, their malevolent presence felt by all who dare approach. The boundary between reality and nightmare dissolves, leaving only pure, unrelenting horror in its wake."


def store_variant(variant_id: str, variant_data: dict):
    """Store a variant for later retrieval"""
    _variant_store[variant_id] = variant_data
    logger.debug(f"Stored variant {variant_id}")


def get_variant(variant_id: str) -> Optional[dict]:
    """Get a variant from store"""
    return _variant_store.get(variant_id)
