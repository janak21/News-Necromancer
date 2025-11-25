# Design Document: AI Voice Narration

## Overview

The AI Voice Narration feature adds immersive audio capabilities to the Spooky RSS System by generating horror-themed voice narrations for spooky content. The system integrates a Text-to-Speech (TTS) API service with the existing backend, implements audio caching for performance, and provides an intuitive audio player interface in the React frontend.

The design follows a three-tier architecture:
1. **Backend Voice Service** - Python module for TTS API integration, audio generation, and caching
2. **API Layer** - RESTful endpoints for narration requests, status checks, and audio delivery
3. **Frontend Audio Player** - React components for voice style selection, playback controls, and user interaction

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │ Voice Style      │  │   Audio Player Component        │ │
│  │ Selector         │  │   - Playback controls           │ │
│  └──────────────────┘  │   - Progress bar                │ │
│                        │   - Speed adjustment            │ │
│                        │   - Download button             │ │
│                        └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Narration Routes                                     │  │
│  │  - POST /api/narration/generate                       │  │
│  │  - GET /api/narration/status/{id}                     │  │
│  │  - GET /api/narration/audio/{id}                      │  │
│  │  - GET /api/narration/voices                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Voice Narration Module (Python)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ TTS Service  │  │ Audio Cache  │  │ Generation      │  │
│  │ - API calls  │  │ - File store │  │ Queue Manager   │  │
│  │ - Streaming  │  │ - LRU evict  │  │ - Priority      │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  TTS API Service │
                    │  (ElevenLabs)    │
                    └──────────────────┘
```

### Data Flow

1. User selects voice style and clicks narration button on a spooky variant
2. Frontend sends POST request to `/api/narration/generate` with content and voice style
3. Backend checks cache for existing audio
4. If not cached, request is queued and TTS API is called
5. Generated audio is cached and URL is returned
6. Frontend polls `/api/narration/status/{id}` for generation progress
7. When ready, audio URL is provided and player loads the audio
8. User controls playback through the audio player interface

## Components and Interfaces

### Backend Components

#### 1. Voice Narration Service (`backend/narration/voice_service.py`)

Core service managing TTS API integration and audio generation.

```python
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

class VoiceStyle(Enum):
    GHOSTLY_WHISPER = "ghostly_whisper"
    DEMONIC_GROWL = "demonic_growl"
    EERIE_NARRATOR = "eerie_narrator"
    POSSESSED_CHILD = "possessed_child"
    ANCIENT_ENTITY = "ancient_entity"

@dataclass
class VoiceConfig:
    voice_id: str
    stability: float
    similarity_boost: float
    style: float
    speed: float

@dataclass
class NarrationRequest:
    content: str
    voice_style: VoiceStyle
    intensity_level: int  # 1-5
    variant_id: str

@dataclass
class NarrationResult:
    narration_id: str
    audio_url: str
    duration: float
    file_size: int
    cached: bool

class VoiceNarrationService:
    def __init__(self, api_key: str, cache_manager: 'AudioCacheManager'):
        self.api_key = api_key
        self.cache_manager = cache_manager
        self.voice_configs = self._initialize_voice_configs()
    
    def _initialize_voice_configs(self) -> Dict[VoiceStyle, VoiceConfig]:
        """Map voice styles to TTS API voice configurations"""
        pass
    
    async def generate_narration(
        self, 
        request: NarrationRequest
    ) -> NarrationResult:
        """Generate audio narration for content"""
        pass
    
    async def _call_tts_api(
        self, 
        text: str, 
        voice_config: VoiceConfig
    ) -> bytes:
        """Call ElevenLabs TTS API with streaming"""
        pass
    
    def _adjust_voice_for_intensity(
        self, 
        base_config: VoiceConfig, 
        intensity: int
    ) -> VoiceConfig:
        """Modify voice parameters based on horror intensity"""
        pass
```

**Key Methods:**
- `generate_narration()`: Main entry point for narration generation
- `_call_tts_api()`: Handles TTS API communication with retry logic
- `_adjust_voice_for_intensity()`: Maps intensity levels to voice parameters

**TTS API Integration:**
- Use ElevenLabs API for high-quality voice synthesis
- Implement streaming to handle large content efficiently
- Support voice cloning for custom horror voices
- Configure voice parameters: stability, similarity_boost, style, speed

#### 2. Audio Cache Manager (`backend/narration/audio_cache.py`)

Manages audio file caching with LRU eviction policy.

```python
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import hashlib

@dataclass
class CacheEntry:
    narration_id: str
    file_path: Path
    created_at: datetime
    last_accessed: datetime
    file_size: int
    variant_id: str
    voice_style: VoiceStyle

class AudioCacheManager:
    def __init__(
        self, 
        cache_dir: Path, 
        max_size_mb: int = 500,
        ttl_days: int = 7
    ):
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl = timedelta(days=ttl_days)
        self.cache_index: Dict[str, CacheEntry] = {}
    
    def get_cache_key(
        self, 
        variant_id: str, 
        voice_style: VoiceStyle
    ) -> str:
        """Generate unique cache key"""
        content = f"{variant_id}:{voice_style.value}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get(self, cache_key: str) -> Optional[Path]:
        """Retrieve cached audio file"""
        pass
    
    async def put(
        self, 
        cache_key: str, 
        audio_data: bytes, 
        metadata: Dict
    ) -> Path:
        """Store audio in cache"""
        pass
    
    async def evict_lru(self, required_space: int):
        """Remove least recently used entries"""
        pass
    
    async def cleanup_expired(self):
        """Remove entries older than TTL"""
        pass
```

**Key Features:**
- LRU eviction when cache exceeds 500MB
- 7-day TTL for cached audio files
- SHA-256 based cache keys from variant_id + voice_style
- Metadata tracking for cache management

#### 3. Generation Queue Manager (`backend/narration/queue_manager.py`)

Manages concurrent narration generation requests with prioritization.

```python
from asyncio import Queue, PriorityQueue
from enum import IntEnum

class Priority(IntEnum):
    HIGH = 1    # Currently visible content
    NORMAL = 2  # Off-screen content
    LOW = 3     # Background prefetch

@dataclass
class QueuedRequest:
    request: NarrationRequest
    priority: Priority
    created_at: datetime
    request_id: str

class GenerationQueueManager:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.queue: PriorityQueue = PriorityQueue()
        self.active_requests: Dict[str, asyncio.Task] = {}
        self.request_status: Dict[str, str] = {}
    
    async def enqueue(
        self, 
        request: NarrationRequest, 
        priority: Priority = Priority.NORMAL
    ) -> str:
        """Add request to generation queue"""
        pass
    
    async def process_queue(self):
        """Process queued requests with concurrency limit"""
        pass
    
    async def cancel_request(self, request_id: str):
        """Cancel a queued or active request"""
        pass
    
    def get_status(self, request_id: str) -> Dict:
        """Get current status of a request"""
        pass
    
    def get_queue_position(self, request_id: str) -> int:
        """Get position in queue"""
        pass
```

**Key Features:**
- Maximum 3 concurrent TTS API calls
- Priority-based queue (visible content first)
- Request cancellation support
- Status tracking and queue position reporting

#### 4. API Routes (`backend/api/routes/narration.py`)

FastAPI endpoints for narration functionality.

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/narration", tags=["narration"])

@router.post("/generate")
async def generate_narration(
    variant_id: str,
    voice_style: str,
    intensity_level: int,
    priority: str = "normal",
    background_tasks: BackgroundTasks
):
    """
    Generate voice narration for a spooky variant.
    Returns request_id for status polling.
    """
    pass

@router.get("/status/{request_id}")
async def get_narration_status(request_id: str):
    """
    Get generation status and progress.
    Returns: {status, progress, audio_url, error}
    """
    pass

@router.get("/audio/{narration_id}")
async def get_audio_file(narration_id: str):
    """
    Serve generated audio file.
    Returns MP3 file with appropriate headers.
    """
    pass

@router.get("/voices")
async def list_voice_styles():
    """
    List available voice styles with preview samples.
    """
    pass

@router.delete("/cancel/{request_id}")
async def cancel_generation(request_id: str):
    """
    Cancel a queued or in-progress generation request.
    """
    pass
```

### Frontend Components

#### 1. Voice Style Selector (`frontend/src/components/VoiceStyleSelector/`)

Component for selecting horror voice styles.

```typescript
interface VoiceStyle {
  id: string;
  name: string;
  description: string;
  previewUrl: string;
  icon: string;
}

interface VoiceStyleSelectorProps {
  selectedStyle: string;
  onStyleChange: (styleId: string) => void;
  intensity: number;
}

export const VoiceStyleSelector: React.FC<VoiceStyleSelectorProps> = ({
  selectedStyle,
  onStyleChange,
  intensity
}) => {
  const [voices, setVoices] = useState<VoiceStyle[]>([]);
  const [playingPreview, setPlayingPreview] = useState<string | null>(null);
  
  // Fetch available voices on mount
  useEffect(() => {
    fetchVoiceStyles().then(setVoices);
  }, []);
  
  const playPreview = (voiceId: string) => {
    // Play preview sample for voice style
  };
  
  return (
    <div className="voice-style-selector">
      {voices.map(voice => (
        <VoiceStyleCard
          key={voice.id}
          voice={voice}
          selected={selectedStyle === voice.id}
          onSelect={() => onStyleChange(voice.id)}
          onPreview={() => playPreview(voice.id)}
          isPlaying={playingPreview === voice.id}
        />
      ))}
    </div>
  );
};
```

#### 2. Audio Player Component (`frontend/src/components/AudioPlayer/`)

Main audio playback interface with controls.

```typescript
interface AudioPlayerProps {
  variantId: string;
  voiceStyle: string;
  intensity: number;
  autoPlay?: boolean;
}

interface AudioPlayerState {
  status: 'idle' | 'generating' | 'ready' | 'playing' | 'paused' | 'error';
  progress: number;
  currentTime: number;
  duration: number;
  playbackRate: number;
  audioUrl: string | null;
  error: string | null;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  variantId,
  voiceStyle,
  intensity,
  autoPlay = false
}) => {
  const [state, setState] = useState<AudioPlayerState>({
    status: 'idle',
    progress: 0,
    currentTime: 0,
    duration: 0,
    playbackRate: 1.0,
    audioUrl: null,
    error: null
  });
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const requestIdRef = useRef<string | null>(null);
  
  const generateNarration = async () => {
    setState(prev => ({ ...prev, status: 'generating', progress: 0 }));
    
    try {
      const response = await api.generateNarration({
        variantId,
        voiceStyle,
        intensityLevel: intensity
      });
      
      requestIdRef.current = response.request_id;
      pollGenerationStatus(response.request_id);
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        status: 'error', 
        error: error.message 
      }));
    }
  };
  
  const pollGenerationStatus = async (requestId: string) => {
    const interval = setInterval(async () => {
      const status = await api.getNarrationStatus(requestId);
      
      if (status.status === 'completed') {
        clearInterval(interval);
        setState(prev => ({
          ...prev,
          status: 'ready',
          audioUrl: status.audio_url
        }));
        
        if (autoPlay) {
          play();
        }
      } else if (status.status === 'failed') {
        clearInterval(interval);
        setState(prev => ({
          ...prev,
          status: 'error',
          error: status.error
        }));
      } else {
        setState(prev => ({
          ...prev,
          progress: status.progress
        }));
      }
    }, 1000);
  };
  
  const play = () => {
    audioRef.current?.play();
    setState(prev => ({ ...prev, status: 'playing' }));
  };
  
  const pause = () => {
    audioRef.current?.pause();
    setState(prev => ({ ...prev, status: 'paused' }));
  };
  
  const seek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };
  
  const setPlaybackRate = (rate: number) => {
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
      setState(prev => ({ ...prev, playbackRate: rate }));
    }
  };
  
  const download = async () => {
    if (state.audioUrl) {
      const link = document.createElement('a');
      link.href = state.audioUrl;
      link.download = `narration-${variantId}.mp3`;
      link.click();
    }
  };
  
  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={state.audioUrl || undefined}
        onTimeUpdate={(e) => {
          setState(prev => ({
            ...prev,
            currentTime: e.currentTarget.currentTime
          }));
        }}
        onLoadedMetadata={(e) => {
          setState(prev => ({
            ...prev,
            duration: e.currentTarget.duration
          }));
        }}
        onEnded={() => {
          setState(prev => ({ ...prev, status: 'ready' }));
        }}
      />
      
      {state.status === 'idle' && (
        <button onClick={generateNarration}>
          Generate Narration
        </button>
      )}
      
      {state.status === 'generating' && (
        <div className="generating-indicator">
          <SpookySpinner />
          <span>Summoning voice... {state.progress}%</span>
        </div>
      )}
      
      {(state.status === 'ready' || state.status === 'playing' || state.status === 'paused') && (
        <>
          <PlaybackControls
            isPlaying={state.status === 'playing'}
            onPlay={play}
            onPause={pause}
          />
          
          <ProgressBar
            currentTime={state.currentTime}
            duration={state.duration}
            onSeek={seek}
          />
          
          <PlaybackRateControl
            rate={state.playbackRate}
            onChange={setPlaybackRate}
          />
          
          <button onClick={download} aria-label="Download narration">
            Download
          </button>
        </>
      )}
      
      {state.status === 'error' && (
        <div className="error-message">
          <span>{state.error}</span>
          <button onClick={generateNarration}>Retry</button>
        </div>
      )}
    </div>
  );
};
```

#### 3. Narration Hook (`frontend/src/hooks/useNarration.ts`)

Custom hook for managing narration state and API calls.

```typescript
interface UseNarrationOptions {
  variantId: string;
  voiceStyle: string;
  intensity: number;
  autoGenerate?: boolean;
}

interface NarrationState {
  status: 'idle' | 'generating' | 'ready' | 'error';
  progress: number;
  audioUrl: string | null;
  error: string | null;
  requestId: string | null;
}

export const useNarration = ({
  variantId,
  voiceStyle,
  intensity,
  autoGenerate = false
}: UseNarrationOptions) => {
  const [state, setState] = useState<NarrationState>({
    status: 'idle',
    progress: 0,
    audioUrl: null,
    error: null,
    requestId: null
  });
  
  const generate = useCallback(async () => {
    // Check cache first
    const cacheKey = `narration_${variantId}_${voiceStyle}`;
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
      const { audioUrl, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;
      
      // Use cached if less than 7 days old
      if (age < 7 * 24 * 60 * 60 * 1000) {
        setState({
          status: 'ready',
          progress: 100,
          audioUrl,
          error: null,
          requestId: null
        });
        return;
      }
    }
    
    // Generate new narration
    setState(prev => ({ ...prev, status: 'generating', progress: 0 }));
    
    try {
      const response = await api.generateNarration({
        variantId,
        voiceStyle,
        intensityLevel: intensity
      });
      
      setState(prev => ({ ...prev, requestId: response.request_id }));
      
      // Poll for completion
      const result = await pollUntilComplete(response.request_id);
      
      // Cache the result
      localStorage.setItem(cacheKey, JSON.stringify({
        audioUrl: result.audio_url,
        timestamp: Date.now()
      }));
      
      setState({
        status: 'ready',
        progress: 100,
        audioUrl: result.audio_url,
        error: null,
        requestId: response.request_id
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error.message
      }));
    }
  }, [variantId, voiceStyle, intensity]);
  
  const cancel = useCallback(async () => {
    if (state.requestId) {
      await api.cancelNarration(state.requestId);
      setState({
        status: 'idle',
        progress: 0,
        audioUrl: null,
        error: null,
        requestId: null
      });
    }
  }, [state.requestId]);
  
  useEffect(() => {
    if (autoGenerate) {
      generate();
    }
  }, [autoGenerate, generate]);
  
  return {
    ...state,
    generate,
    cancel
  };
};
```

## Data Models

### Backend Models

```python
# backend/models/narration_models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class VoiceStyleEnum(str, Enum):
    GHOSTLY_WHISPER = "ghostly_whisper"
    DEMONIC_GROWL = "demonic_growl"
    EERIE_NARRATOR = "eerie_narrator"
    POSSESSED_CHILD = "possessed_child"
    ANCIENT_ENTITY = "ancient_entity"

class GenerationStatus(str, Enum):
    QUEUED = "queued"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NarrationGenerateRequest(BaseModel):
    variant_id: str = Field(..., description="ID of the spooky variant")
    voice_style: VoiceStyleEnum
    intensity_level: int = Field(..., ge=1, le=5)
    priority: str = Field(default="normal")

class NarrationGenerateResponse(BaseModel):
    request_id: str
    status: GenerationStatus
    estimated_time: Optional[int] = None  # seconds
    queue_position: Optional[int] = None

class NarrationStatusResponse(BaseModel):
    request_id: str
    status: GenerationStatus
    progress: int = Field(..., ge=0, le=100)
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class VoiceStyleInfo(BaseModel):
    id: str
    name: str
    description: str
    preview_url: str
    icon: str
    recommended_intensity: int
```

### Frontend Types

```typescript
// frontend/src/types/narration.ts

export enum VoiceStyle {
  GHOSTLY_WHISPER = 'ghostly_whisper',
  DEMONIC_GROWL = 'demonic_growl',
  EERIE_NARRATOR = 'eerie_narrator',
  POSSESSED_CHILD = 'possessed_child',
  ANCIENT_ENTITY = 'ancient_entity'
}

export enum GenerationStatus {
  QUEUED = 'queued',
  GENERATING = 'generating',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface NarrationRequest {
  variantId: string;
  voiceStyle: VoiceStyle;
  intensityLevel: number;
  priority?: 'high' | 'normal' | 'low';
}

export interface NarrationStatus {
  requestId: string;
  status: GenerationStatus;
  progress: number;
  audioUrl?: string;
  duration?: number;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface VoiceStyleInfo {
  id: string;
  name: string;
  description: string;
  previewUrl: string;
  icon: string;
  recommendedIntensity: number;
}
```

## Error Handling

### Backend Error Handling

1. **TTS API Failures**
   - Implement exponential backoff retry (3 attempts)
   - Fallback to alternative voice if primary fails
   - Log detailed error context for debugging
   - Return user-friendly error messages

2. **Rate Limiting**
   - Track API quota usage
   - Queue requests when approaching limits
   - Inform users of estimated wait times
   - Implement request prioritization

3. **Cache Failures**
   - Gracefully handle disk space issues
   - Regenerate if cached file is corrupted
   - Log cache misses and evictions

4. **Queue Management**
   - Handle queue overflow gracefully
   - Provide clear feedback on queue position
   - Allow request cancellation
   - Clean up abandoned requests

### Frontend Error Handling

1. **Network Errors**
   - Display retry button with exponential backoff
   - Show offline indicator
   - Cache requests for retry when online

2. **Generation Failures**
   - Show user-friendly error messages
   - Provide alternative actions (try different voice)
   - Log errors for analytics

3. **Playback Errors**
   - Handle audio format incompatibilities
   - Provide fallback for unsupported browsers
   - Show clear error states

## Testing Strategy

### Backend Testing

1. **Unit Tests**
   - Voice service TTS API integration
   - Cache manager LRU eviction logic
   - Queue manager prioritization
   - Voice parameter adjustment for intensity

2. **Integration Tests**
   - End-to-end narration generation flow
   - Cache hit/miss scenarios
   - Queue processing with concurrent requests
   - API endpoint responses

3. **Performance Tests**
   - Concurrent generation load testing
   - Cache performance under load
   - API response times
   - Memory usage with large queues

### Frontend Testing

1. **Component Tests**
   - Audio player controls functionality
   - Voice style selector interactions
   - Progress bar updates
   - Error state rendering

2. **Hook Tests**
   - useNarration state management
   - Cache behavior
   - Polling logic
   - Cleanup on unmount

3. **Integration Tests**
   - Full narration generation flow
   - Audio playback functionality
   - Download functionality
   - Keyboard controls

4. **Accessibility Tests**
   - ARIA labels on all controls
   - Keyboard navigation
   - Screen reader announcements
   - Focus management

### Manual Testing Scenarios

1. Generate narration for various content lengths
2. Test all voice styles at different intensities
3. Verify cache behavior across sessions
4. Test queue management with multiple requests
5. Verify playback controls (play, pause, seek, speed)
6. Test download functionality
7. Verify error handling for API failures
8. Test on different browsers and devices
9. Verify accessibility with screen readers
10. Test keyboard-only navigation

## Performance Considerations

1. **Audio Streaming**
   - Stream large audio files instead of loading entirely
   - Use chunked transfer encoding
   - Implement progressive loading

2. **Caching Strategy**
   - Browser localStorage for URL caching (7 days)
   - Server-side file cache (500MB limit)
   - CDN integration for audio delivery
   - Cache invalidation on content updates

3. **Queue Optimization**
   - Limit concurrent TTS API calls (3 max)
   - Prioritize visible content
   - Prefetch for likely next requests
   - Cancel abandoned requests

4. **Frontend Optimization**
   - Lazy load audio player component
   - Debounce voice style changes
   - Optimize re-renders with React.memo
   - Use Web Workers for audio processing if needed

## Security Considerations

1. **API Key Protection**
   - Store TTS API keys in environment variables
   - Never expose keys in frontend code
   - Rotate keys periodically

2. **Content Validation**
   - Sanitize text content before TTS generation
   - Limit content length (10,000 characters)
   - Validate voice style parameters

3. **Rate Limiting**
   - Implement per-user rate limits
   - Prevent abuse of generation endpoints
   - Monitor for unusual patterns

4. **Audio File Security**
   - Generate unique, non-guessable URLs
   - Implement expiring signed URLs
   - Validate file access permissions
   - Scan for malicious content

## Configuration

### Environment Variables

```bash
# Backend (.env)
ELEVENLABS_API_KEY=your_api_key_here
NARRATION_CACHE_DIR=/var/cache/spooky-rss/narration
NARRATION_CACHE_MAX_SIZE_MB=500
NARRATION_CACHE_TTL_DAYS=7
NARRATION_MAX_CONCURRENT=3
NARRATION_MAX_CONTENT_LENGTH=10000
```

### Voice Style Configuration

```python
# backend/narration/voice_configs.py

VOICE_STYLE_CONFIGS = {
    VoiceStyle.GHOSTLY_WHISPER: {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # ElevenLabs voice ID
        "base_stability": 0.3,
        "base_similarity_boost": 0.8,
        "base_style": 0.6,
        "base_speed": 0.9,
        "intensity_modifiers": {
            1: {"stability": 0.5, "speed": 1.0},
            2: {"stability": 0.4, "speed": 0.95},
            3: {"stability": 0.3, "speed": 0.9},
            4: {"stability": 0.2, "speed": 0.85},
            5: {"stability": 0.1, "speed": 0.8}
        }
    },
    # ... other voice styles
}
```

## Migration and Deployment

1. **Database Migrations**
   - Add narration_requests table for tracking
   - Add narration_cache_index table for cache management

2. **Deployment Steps**
   - Deploy backend with new narration module
   - Create cache directory with proper permissions
   - Configure TTS API credentials
   - Deploy frontend with audio player components
   - Test end-to-end functionality
   - Monitor initial usage and performance

3. **Rollback Plan**
   - Feature flag for narration functionality
   - Graceful degradation if TTS API unavailable
   - Maintain backward compatibility with existing features
