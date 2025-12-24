# Scripts Directory

Place your JSON script files here.

## Example Script

See `example_scene.json` for a complete example of the JSON schema.

## Script Structure

Each script must contain:

1. **metadata**: Video resolution and FPS
2. **scenes**: Array of scene objects, each containing:
   - `background`: Path to background image (relative to assets/)
   - `actors`: Array of actor definitions
   - `timeline`: Array of timeline events
   - `audio`: Audio configuration (optional)

## Running Scripts

```bash
python main.py scripts/your_script.json
```

