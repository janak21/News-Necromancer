# AudioPlayer Component

The AudioPlayer component provides a complete audio narration interface for the Spooky RSS System, supporting AI-generated voice narration with full playback controls.

## Features

- **Narration Generation**: Generate AI voice narration for spooky content
- **Playback Controls**: Play, pause, and seek through audio
- **Speed Adjustment**: Control playback speed from 0.5x to 2.0x
- **Download Support**: Download narrations as MP3 files
- **Progress Tracking**: Real-time generation progress with visual feedback
- **Error Handling**: Graceful error handling with retry functionality
- **Background Playback**: Continue playback while navigating
- **Accessibility**: Full keyboard support and ARIA labels

## Usage

```tsx
import { AudioPlayer } from '../components/AudioPlayer';
import { VoiceStyle } from '../types/narration';

function MyComponent() {
  return (
    <AudioPlayer
      variantId="variant-123"
      voiceStyle={VoiceStyle.GHOSTLY_WHISPER}
      intensity={3}
      autoPlay={false}
    />
  );
}
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `variantId` | `string` | Yes | - | ID of the spooky variant to narrate |
| `voiceStyle` | `VoiceStyle` | Yes | - | Horror voice style to use |
| `intensity` | `number` | Yes | - | Horror intensity level (1-5) |
| `autoPlay` | `boolean` | No | `false` | Auto-play when audio is ready |
| `className` | `string` | No | `''` | Additional CSS classes |

## States

The AudioPlayer handles multiple states:

1. **Idle**: Shows "Generate Narration" button
2. **Generating**: Shows progress indicator with cancel option
3. **Ready**: Shows full playback controls
4. **Playing**: Audio is actively playing
5. **Error**: Shows error message with retry button

## Playback Controls

- **Play/Pause Button**: Toggle audio playback
- **Seek Bar**: Click or drag to jump to specific positions
- **Time Display**: Shows current time and total duration
- **Speed Control**: Dropdown to adjust playback rate
- **Download Button**: Save narration as MP3 file

## Keyboard Support

The component supports standard HTML5 audio keyboard controls through the native audio element.

## Requirements Satisfied

- **1.1**: Generate audio narration for spooky variants
- **1.5**: Provide playable audio URL when generation completes
- **3.1**: Play, pause, and stop controls
- **3.2**: Display playback position and duration with seek bar
- **3.3**: Playback speed adjustment (0.5x to 2.0x)
- **3.4**: Background playback support
- **3.5**: Seek bar for jumping to positions
- **5.1**: Display narration status during generation
- **5.2**: Show progress indicator during generation
- **5.3**: Estimate and display remaining time
- **5.4**: Display error messages on failure
- **5.5**: Automatically enable playback when ready
- **9.1**: Download button for narrations
- **9.2**: Provide audio in MP3 format
- **9.3**: Include metadata in downloads
- **9.4**: Generate descriptive filenames
- **9.5**: Track download status

## Styling

The component uses CSS custom properties and follows the dark horror theme of the application. It's fully responsive and includes accessibility features like high contrast mode support and reduced motion preferences.

## Testing

The component includes comprehensive unit tests covering:
- Idle state rendering
- Generation triggering
- Progress display
- Error handling
- Playback controls
- Speed adjustment
- Download functionality

Run tests with:
```bash
npm run test -- AudioPlayer.test.tsx
```
