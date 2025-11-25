# Implementation Plan

- [x] 1. Set up backend narration module structure and dependencies
  - Create directory structure: `backend/narration/` with `__init__.py`, `voice_service.py`, `audio_cache.py`, `queue_manager.py`
  - Add required dependencies to `backend/requirements.txt`: `elevenlabs`, `aiofiles`, `pydantic`
  - Create configuration file for voice style mappings
  - _Requirements: 1.1, 1.2, 2.1_

- [x] 2. Implement data models for narration
  - [x] 2.1 Create Pydantic models in `backend/models/narration_models.py`
    - Write `VoiceStyleEnum`, `GenerationStatus`, `NarrationGenerateRequest`, `NarrationGenerateResponse`, `NarrationStatusResponse`, `VoiceStyleInfo` models
    - Add validation rules for intensity levels (1-5) and content length (max 10,000 characters)
    - _Requirements: 1.3, 2.1, 2.2, 7.1_

- [x] 3. Implement audio cache manager
  - [x] 3.1 Create `AudioCacheManager` class in `backend/narration/audio_cache.py`
    - Implement cache key generation using SHA-256 hash of variant_id + voice_style
    - Write `get()` method to retrieve cached audio files
    - Write `put()` method to store audio with metadata
    - Implement LRU eviction logic when cache exceeds 500MB
    - Implement TTL-based cleanup for entries older than 7 days
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Implement generation queue manager
  - [x] 4.1 Create `GenerationQueueManager` class in `backend/narration/queue_manager.py`
    - Implement priority queue using `asyncio.PriorityQueue`
    - Write `enqueue()` method with priority support (HIGH, NORMAL, LOW)
    - Write `process_queue()` method limiting concurrent processing to 3 requests
    - Implement `cancel_request()` method for canceling queued/active requests
    - Write `get_status()` and `get_queue_position()` methods for status tracking
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5. Implement voice narration service with TTS API integration
  - [x] 5.1 Create `VoiceNarrationService` class in `backend/narration/voice_service.py`
    - Initialize ElevenLabs client with API key from environment variables
    - Implement `_initialize_voice_configs()` mapping voice styles to ElevenLabs voice IDs
    - Write `_adjust_voice_for_intensity()` to modify voice parameters based on horror intensity (1-5)
    - Implement `_call_tts_api()` with streaming support and exponential backoff retry logic (3 attempts)
    - Write main `generate_narration()` method coordinating cache check, API call, and storage
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 2.1, 2.3, 2.4, 6.1, 6.2, 6.3, 10.1, 10.2_

- [x] 6. Create narration API routes
  - [x] 6.1 Implement FastAPI routes in `backend/api/routes/narration.py`
    - Write `POST /api/narration/generate` endpoint accepting variant_id, voice_style, intensity_level, priority
    - Write `GET /api/narration/status/{request_id}` endpoint returning generation status and progress
    - Write `GET /api/narration/audio/{narration_id}` endpoint serving MP3 files with proper headers
    - Write `GET /api/narration/voices` endpoint listing available voice styles with preview URLs
    - Write `DELETE /api/narration/cancel/{request_id}` endpoint for canceling requests
    - Register router in main FastAPI application
    - _Requirements: 1.1, 1.5, 2.1, 2.5, 5.1, 5.2, 5.3, 7.4, 10.3_

- [x] 7. Create frontend TypeScript types for narration
  - [x] 7.1 Define types in `frontend/src/types/narration.ts`
    - Write `VoiceStyle` enum matching backend voice styles
    - Write `GenerationStatus` enum for tracking narration state
    - Define `NarrationRequest`, `NarrationStatus`, `VoiceStyleInfo` interfaces
    - _Requirements: 2.1, 5.1_

- [x] 8. Implement narration API client methods
  - [x] 8.1 Add narration methods to `frontend/src/services/api.ts`
    - Write `generateNarration()` method calling POST /api/narration/generate
    - Write `getNarrationStatus()` method calling GET /api/narration/status/{request_id}
    - Write `getVoiceStyles()` method calling GET /api/narration/voices
    - Write `cancelNarration()` method calling DELETE /api/narration/cancel/{request_id}
    - _Requirements: 1.1, 5.1, 7.4_

- [x] 9. Create useNarration custom hook
  - [x] 9.1 Implement hook in `frontend/src/hooks/useNarration.ts`
    - Write state management for narration status, progress, audioUrl, error
    - Implement `generate()` function with localStorage caching (7-day TTL)
    - Implement polling logic using `getNarrationStatus()` with 1-second intervals
    - Write `cancel()` function for canceling generation requests
    - Add auto-generation support via `autoGenerate` option
    - _Requirements: 1.1, 1.5, 4.1, 4.2, 5.1, 5.2, 5.3, 7.4_

- [x] 10. Create VoiceStyleSelector component
  - [x] 10.1 Implement component in `frontend/src/components/VoiceStyleSelector/`
    - Create `VoiceStyleSelector.tsx` with voice style cards display
    - Implement voice preview playback functionality
    - Add visual indication for selected voice style
    - Create `VoiceStyleSelector.css` with dark theme styling
    - Create `VoiceStyleCard` sub-component for individual voice styles
    - Create `index.ts` barrel export
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 6.5_

- [x] 11. Create AudioPlayer component
  - [x] 11.1 Implement main player in `frontend/src/components/AudioPlayer/`
    - Create `AudioPlayer.tsx` with audio element and state management
    - Implement `generateNarration()` function triggering narration generation
    - Implement `pollGenerationStatus()` for status updates
    - Write playback control functions: `play()`, `pause()`, `seek()`, `setPlaybackRate()`
    - Implement `download()` function for saving narration as MP3
    - Add loading state display with progress indicator
    - Add error state display with retry button
    - Create `AudioPlayer.css` with themed styling
    - Create `index.ts` barrel export
    - _Requirements: 1.1, 1.5, 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 12. Create playback control sub-components
  - [x] 12.1 Implement PlaybackControls component
    - Create `PlaybackControls.tsx` with play/pause button
    - Add ARIA labels for accessibility
    - Style with dark theme
    - _Requirements: 3.1, 8.1, 8.4_
  
  - [x] 12.2 Implement ProgressBar component
    - Create `ProgressBar.tsx` with seek functionality
    - Display current time and total duration
    - Add click-to-seek interaction
    - Style with horror theme
    - _Requirements: 3.2, 3.5_
  
  - [x] 12.3 Implement PlaybackRateControl component
    - Create `PlaybackRateControl.tsx` with speed adjustment (0.5x to 2.0x)
    - Add preset speed buttons and custom slider
    - Display current playback rate
    - _Requirements: 3.3_

- [x] 13. Integrate AudioPlayer into SpookyCard component
  - [x] 13.1 Add narration controls to SpookyCard
    - Import and render `AudioPlayer` component within each spooky variant card
    - Pass variant_id, voice_style, and intensity props to AudioPlayer
    - Add toggle button to show/hide audio player
    - Update `SpookyCard.css` to accommodate audio player layout
    - _Requirements: 1.1, 3.4_

- [x] 14. Add voice style preferences to user preferences
  - [x] 14.1 Update preferences panel with voice settings
    - Add voice style selector to `PreferencesPanel.tsx`
    - Implement preference persistence in localStorage
    - Add "auto-match intensity" toggle option
    - Update `PreferencesPanel.css` for new controls
    - _Requirements: 2.3, 2.5, 6.4_

- [ ]* 15. Implement keyboard controls for audio player
  - [ ]* 15.1 Add keyboard event handlers to AudioPlayer
    - Implement spacebar for play/pause
    - Implement arrow keys for seeking (left/right: ±5 seconds)
    - Implement keyboard shortcuts for speed adjustment (e.g., Shift+Up/Down)
    - Add visible focus indicators on all controls
    - Implement ARIA live regions for state announcements
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 16. Add environment configuration for TTS API
  - [x] 16.1 Configure backend environment variables
    - Add `ELEVENLABS_API_KEY` to `.env` file
    - Add `NARRATION_CACHE_DIR`, `NARRATION_CACHE_MAX_SIZE_MB`, `NARRATION_CACHE_TTL_DAYS` settings
    - Add `NARRATION_MAX_CONCURRENT`, `NARRATION_MAX_CONTENT_LENGTH` settings
    - Update `.env.example` with narration configuration template
    - _Requirements: 1.1, 1.2, 4.3, 4.5, 7.2_

- [x] 17. Create voice configuration file
  - [x] 17.1 Define voice style mappings
    - Create `backend/narration/voice_configs.py` with `VOICE_STYLE_CONFIGS` dictionary
    - Map each voice style to ElevenLabs voice_id and base parameters
    - Define intensity modifiers for each voice style (levels 1-5)
    - Include stability, similarity_boost, style, and speed parameters
    - _Requirements: 2.1, 2.2, 2.4, 6.1, 6.2, 6.3_

- [x] 18. Implement error handling and retry logic
  - [x] 18.1 Add comprehensive error handling to voice service
    - Implement exponential backoff retry for TTS API failures (3 attempts)
    - Add detailed error logging with context information
    - Implement rate limit detection and queue management
    - Add fallback behavior for extended API outages
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 18.2 Add error handling to frontend components
    - Display user-friendly error messages in AudioPlayer
    - Implement retry button with exponential backoff
    - Add offline detection and queuing
    - Log errors for analytics
    - _Requirements: 5.4, 5.5_

- [x] 19. Update data models to include narration metadata
  - [x] 19.1 Extend SpookyVariant model
    - Add optional `narration_url` field to `backend/models/data_models.py`
    - Add `narration_generated_at` timestamp field
    - Update API responses to include narration metadata
    - _Requirements: 1.5_

- [ ]* 20. Create database migrations for narration tracking
  - [ ]* 20.1 Add narration tables
    - Create migration for `narration_requests` table with columns: id, variant_id, voice_style, intensity, status, created_at, completed_at, audio_url, error
    - Create migration for `narration_cache_index` table with columns: cache_key, file_path, created_at, last_accessed, file_size, variant_id, voice_style
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 21. Implement background cleanup tasks
  - [x] 21.1 Create scheduled cleanup job
    - Write background task in `backend/narration/cleanup.py` for expired cache cleanup
    - Implement abandoned request cleanup (requests older than 1 hour in queued/generating state)
    - Schedule cleanup to run every 6 hours
    - _Requirements: 4.3, 4.5_

- [x] 22. Add narration feature to README documentation
  - [x] 22.1 Document narration feature
    - Add "AI Voice Narration" section to `README.md`
    - Document available voice styles and their characteristics
    - Provide setup instructions for ElevenLabs API key
    - Document keyboard shortcuts and accessibility features
    - _Requirements: 2.1, 2.2, 8.1, 8.2, 8.3_
