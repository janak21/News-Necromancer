"""
Voice style configuration mappings for TTS API.

This module defines the voice style configurations including:
- ElevenLabs voice IDs for each horror voice style
- Base voice parameters (stability, similarity_boost, style, speed)
- Intensity modifiers for adjusting voice characteristics based on horror intensity (1-5)
"""

from enum import Enum


class VoiceStyle(Enum):
    """Available horror voice styles for narration."""
    GHOSTLY_WHISPER = "ghostly_whisper"
    DEMONIC_GROWL = "demonic_growl"
    EERIE_NARRATOR = "eerie_narrator"
    POSSESSED_CHILD = "possessed_child"
    ANCIENT_ENTITY = "ancient_entity"


# Voice style configurations mapping each horror voice style to TTS parameters
VOICE_STYLE_CONFIGS = {
    VoiceStyle.GHOSTLY_WHISPER: {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # ElevenLabs voice ID (placeholder)
        "name": "Ghostly Whisper",
        "description": "A haunting, ethereal whisper that sends chills down your spine",
        "base_stability": 0.3,
        "base_similarity_boost": 0.8,
        "base_style": 0.6,
        "base_speed": 0.9,
        "intensity_modifiers": {
            1: {"stability": 0.5, "speed": 1.0, "style": 0.3},
            2: {"stability": 0.4, "speed": 0.95, "style": 0.4},
            3: {"stability": 0.3, "speed": 0.9, "style": 0.6},
            4: {"stability": 0.2, "speed": 0.85, "style": 0.7},
            5: {"stability": 0.1, "speed": 0.8, "style": 0.9}
        }
    },
    VoiceStyle.DEMONIC_GROWL: {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # ElevenLabs voice ID (placeholder)
        "name": "Demonic Growl",
        "description": "A deep, menacing growl from the depths of darkness",
        "base_stability": 0.4,
        "base_similarity_boost": 0.7,
        "base_style": 0.8,
        "base_speed": 0.85,
        "intensity_modifiers": {
            1: {"stability": 0.6, "speed": 0.95, "style": 0.5},
            2: {"stability": 0.5, "speed": 0.9, "style": 0.6},
            3: {"stability": 0.4, "speed": 0.85, "style": 0.8},
            4: {"stability": 0.3, "speed": 0.8, "style": 0.9},
            5: {"stability": 0.2, "speed": 0.75, "style": 1.0}
        }
    },
    VoiceStyle.EERIE_NARRATOR: {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # ElevenLabs voice ID (placeholder)
        "name": "Eerie Narrator",
        "description": "A calm yet unsettling voice that tells tales of terror",
        "base_stability": 0.6,
        "base_similarity_boost": 0.75,
        "base_style": 0.5,
        "base_speed": 0.95,
        "intensity_modifiers": {
            1: {"stability": 0.7, "speed": 1.0, "style": 0.3},
            2: {"stability": 0.65, "speed": 0.98, "style": 0.4},
            3: {"stability": 0.6, "speed": 0.95, "style": 0.5},
            4: {"stability": 0.5, "speed": 0.9, "style": 0.6},
            5: {"stability": 0.4, "speed": 0.85, "style": 0.7}
        }
    },
    VoiceStyle.POSSESSED_CHILD: {
        "voice_id": "jBpfuIE2acCO8z3wKNLl",  # ElevenLabs voice ID (placeholder)
        "name": "Possessed Child",
        "description": "An innocent voice twisted by malevolent forces",
        "base_stability": 0.2,
        "base_similarity_boost": 0.85,
        "base_style": 0.7,
        "base_speed": 1.0,
        "intensity_modifiers": {
            1: {"stability": 0.4, "speed": 1.05, "style": 0.4},
            2: {"stability": 0.3, "speed": 1.02, "style": 0.5},
            3: {"stability": 0.2, "speed": 1.0, "style": 0.7},
            4: {"stability": 0.15, "speed": 0.95, "style": 0.8},
            5: {"stability": 0.1, "speed": 0.9, "style": 1.0}
        }
    },
    VoiceStyle.ANCIENT_ENTITY: {
        "voice_id": "onwK4e9ZLuTAKqWW03F9",  # Original voice (Attenborough-like)
        "name": "Ancient Entity",
        "description": "A timeless, otherworldly voice from beyond comprehension",
        "base_stability": 0.65,  # Higher for smoother, more natural delivery
        "base_similarity_boost": 0.75,  # Higher for better voice clarity
        "base_style": 0.5,  # Moderate style for natural narration
        "base_speed": 0.9,  # Slightly slower for dramatic effect
        "intensity_modifiers": {
            1: {"stability": 0.6, "speed": 0.9, "style": 0.6},
            2: {"stability": 0.55, "speed": 0.85, "style": 0.7},
            3: {"stability": 0.5, "speed": 0.8, "style": 0.9},
            4: {"stability": 0.4, "speed": 0.75, "style": 1.0},
            5: {"stability": 0.3, "speed": 0.7, "style": 1.0}
        }
    }
}


def get_voice_config(voice_style: VoiceStyle) -> dict:
    """
    Get the configuration for a specific voice style.
    
    Args:
        voice_style: The voice style to retrieve configuration for
        
    Returns:
        Dictionary containing voice configuration parameters
        
    Raises:
        KeyError: If voice style is not configured
    """
    if voice_style not in VOICE_STYLE_CONFIGS:
        raise KeyError(f"Voice style {voice_style} not found in configurations")
    
    return VOICE_STYLE_CONFIGS[voice_style]


def get_all_voice_styles() -> list:
    """
    Get a list of all available voice styles with their metadata.
    
    Returns:
        List of dictionaries containing voice style information
    """
    return [
        {
            "id": style.value,
            "name": config["name"],
            "description": config["description"],
            "voice_id": config["voice_id"]
        }
        for style, config in VOICE_STYLE_CONFIGS.items()
    ]
