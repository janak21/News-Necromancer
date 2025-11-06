"""
User preferences management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ...models.data_models import UserPreferences, StatusResponse, HorrorType

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for demo (would use database in production)
user_preferences_store: Dict[str, UserPreferences] = {}

class PreferencesRequest(BaseModel):
    """Request model for updating user preferences"""
    user_id: str
    preferred_horror_types: Optional[list] = None
    intensity_level: Optional[int] = None
    content_filters: Optional[list] = None
    notification_settings: Optional[dict] = None
    theme_customizations: Optional[dict] = None

@router.post("/", response_model=dict)
async def update_user_preferences(request: PreferencesRequest):
    """
    Update user preferences for content personalization
    
    Args:
        request: User preferences update request
        
    Returns:
        Status response with updated preferences
    """
    try:
        # Validate intensity level
        if request.intensity_level is not None and not (1 <= request.intensity_level <= 5):
            raise HTTPException(
                status_code=400,
                detail="Intensity level must be between 1 and 5"
            )
        
        # Convert horror type strings to enums if provided
        horror_types = []
        if request.preferred_horror_types:
            for ht_str in request.preferred_horror_types:
                try:
                    horror_type = HorrorType(ht_str.lower())
                    horror_types.append(horror_type)
                except ValueError:
                    logger.warning(f"Invalid horror type: {ht_str}")
        
        # Create or update user preferences
        if request.user_id in user_preferences_store:
            # Update existing preferences
            existing_prefs = user_preferences_store[request.user_id]
            
            if horror_types:
                existing_prefs.preferred_horror_types = horror_types
            if request.intensity_level is not None:
                existing_prefs.intensity_level = request.intensity_level
            if request.content_filters is not None:
                existing_prefs.content_filters = request.content_filters
            if request.notification_settings is not None:
                existing_prefs.notification_settings = request.notification_settings
            if request.theme_customizations is not None:
                existing_prefs.theme_customizations = request.theme_customizations
            
            preferences = existing_prefs
        else:
            # Create new preferences
            preferences = UserPreferences(
                user_id=request.user_id,
                preferred_horror_types=horror_types,
                intensity_level=request.intensity_level or 3,
                content_filters=request.content_filters or [],
                notification_settings=request.notification_settings or {},
                theme_customizations=request.theme_customizations or {}
            )
        
        # Store preferences
        user_preferences_store[request.user_id] = preferences
        
        logger.info(f"👻 Updated preferences for user {request.user_id}")
        
        response = StatusResponse(
            success=True,
            message=f"Successfully updated preferences for user {request.user_id}",
            data=preferences.to_dict()
        )
        
        return response.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.get("/{user_id}", response_model=dict)
async def get_user_preferences(user_id: str):
    """
    Get user preferences by user ID
    
    Args:
        user_id: User identifier
        
    Returns:
        User preferences or default preferences if not found
    """
    try:
        if user_id in user_preferences_store:
            preferences = user_preferences_store[user_id]
            return {
                "success": True,
                "user_id": user_id,
                "preferences": preferences.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Return default preferences
            default_preferences = UserPreferences(user_id=user_id)
            return {
                "success": True,
                "user_id": user_id,
                "preferences": default_preferences.to_dict(),
                "is_default": True,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"💀 Error retrieving preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve preferences: {str(e)}"
        )

@router.delete("/{user_id}", response_model=dict)
async def delete_user_preferences(user_id: str):
    """
    Delete user preferences
    
    Args:
        user_id: User identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        if user_id in user_preferences_store:
            del user_preferences_store[user_id]
            logger.info(f"🗑️ Deleted preferences for user {user_id}")
            
            response = StatusResponse(
                success=True,
                message=f"Successfully deleted preferences for user {user_id}"
            )
        else:
            response = StatusResponse(
                success=False,
                message=f"No preferences found for user {user_id}"
            )
        
        return response.to_dict()
        
    except Exception as e:
        logger.error(f"💀 Error deleting preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete preferences: {str(e)}"
        )

@router.get("/", response_model=dict)
async def list_all_preferences():
    """
    List all stored user preferences (admin endpoint)
    
    Returns:
        List of all user preferences
    """
    try:
        all_preferences = {}
        for user_id, preferences in user_preferences_store.items():
            all_preferences[user_id] = preferences.to_dict()
        
        return {
            "success": True,
            "total_users": len(all_preferences),
            "preferences": all_preferences,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"💀 Error listing preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list preferences: {str(e)}"
        )

@router.get("/horror-types/available")
async def get_available_horror_types():
    """
    Get list of available horror types for preferences
    
    Returns:
        List of available horror types with descriptions
    """
    horror_types_info = {
        "gothic": {
            "name": "Gothic Horror",
            "description": "Haunted locations, ancient curses, supernatural entities",
            "themes": ["haunted mansions", "family secrets", "ancestral sins"]
        },
        "psychological": {
            "name": "Psychological Horror", 
            "description": "Mind manipulation, reality distortion, paranoia",
            "themes": ["psychological breakdown", "identity crisis", "memory loss"]
        },
        "cosmic": {
            "name": "Cosmic Horror",
            "description": "Otherworldly forces, incomprehensible entities",
            "themes": ["alien influences", "dimensional rifts", "eldritch beings"]
        },
        "folk": {
            "name": "Folk Horror",
            "description": "Rural mysteries, pagan rituals, nature-based threats",
            "themes": ["ancient traditions", "forest spirits", "harvest curses"]
        },
        "supernatural": {
            "name": "Supernatural Horror",
            "description": "Vengeful spirits, ghostly apparitions, spectral warnings",
            "themes": ["poltergeist activity", "spiritual possession", "restless souls"]
        }
    }
    
    return {
        "success": True,
        "horror_types": horror_types_info,
        "intensity_levels": {
            "1": "Subtle and atmospheric",
            "2": "Mildly unsettling", 
            "3": "Moderately scary",
            "4": "Quite frightening",
            "5": "Intensely terrifying"
        }
    }