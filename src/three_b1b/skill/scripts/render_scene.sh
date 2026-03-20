#!/bin/bash
# Render a single Manim scene with quality selection.
# Usage: ./render_scene.sh <file.py> <SceneName> [quality]
# quality: l (low/fast), m (medium), h (high/1080p), k (4K)

set -euo pipefail

FILE="${1:?Usage: render_scene.sh <file.py> <SceneName> [quality]}"
SCENE="${2:?Usage: render_scene.sh <file.py> <SceneName> [quality]}"
QUALITY="${3:-l}"

echo "Rendering $SCENE from $FILE at -q$QUALITY..."
manim -q"$QUALITY" "$FILE" "$SCENE"

# Show output location
OUTPUT=$(find media/videos -name "${SCENE}.mp4" ! -path "*/partial_*" -newer "$FILE" 2>/dev/null | head -1)
if [ -n "$OUTPUT" ]; then
    echo "Output: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
else
    echo "Warning: output file not found"
fi
