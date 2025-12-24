# Assets Directory

Place your media assets here.

## Directory Structure

```
assets/
├── backgrounds/    # Background images (PNG, JPG)
├── characters/     # Character images (PNG with alpha channel)
└── audio/          # Audio files (WAV, MP3)
    ├── dialog/     # Dialog audio files
    ├── music/      # Background music
    └── sfx/        # Sound effects
```

## Asset Requirements

### Background Images
- Format: PNG or JPG
- Recommended resolution: Match your script metadata resolution
- No alpha channel required

### Character Images
- Format: PNG with alpha channel (transparent background)
- Recommended: High resolution for scaling
- Center characters in the image frame

### Audio Files
- Formats: WAV (recommended for dialog), MP3 (for music)
- Dialog: Clear, normalized audio
- Music: Can be looped (set `loop: true` in script)
- SFX: Short audio clips

## Example Asset Organization

```
assets/
├── backgrounds/
│   └── scene1_bg.png
├── characters/
│   ├── character_a.png
│   └── character_b.png
└── audio/
    ├── dialog_character_a_line1.wav
    ├── dialog_character_b_line1.wav
    └── background_music.mp3
```

