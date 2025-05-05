#!/bin/bash

# Script to download Big Buck Bunny, trim it, create multiple representations, 
# segment it for DASH, and place it in the web server directory.

SOURCE_VIDEO_URL="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
SOURCE_VIDEO_FILE="BigBuckBunny.mp4"
TRIMMED_VIDEO_FILE="bbb_30s.mp4"
DURATION=30 # Duration in seconds to trim to
OUTPUT_DIR="/var/www/html/videos/dash"
TEMP_DIR="/tmp/bbb_processing"

# --- Representaions ---
# Format: resolution height bitrate(video) bitrate(audio)
REPS=(
    "426x240 400k 64k"
    "640x360 800k 96k"
    "854x480 1200k 128k"
    "1280x720 2500k 192k" 
)
# Note: 1920x1080 might be too heavy for typical Mininet tests, using 720p as max.

# --- Installation ---
echo "Installing dependencies: ffmpeg and gpac (MP4Box)..."
sudo apt-get update
sudo apt-get install -y ffmpeg gpac wget

# --- Preparation ---
echo "Setting up directories..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
sudo mkdir -p "$OUTPUT_DIR"
cd "$TEMP_DIR" || exit 1

# --- Download ---
if [ ! -f "$SOURCE_VIDEO_FILE" ]; then
    echo "Downloading Big Buck Bunny source video..."
    wget "$SOURCE_VIDEO_URL" -O "$SOURCE_VIDEO_FILE"
else
    echo "Source video already downloaded."
fi

# --- Trim ---
echo "Trimming video to first $DURATION seconds..."
ffmpeg -y -i "$SOURCE_VIDEO_FILE" -ss 0 -t "$DURATION" -c copy "$TRIMMED_VIDEO_FILE"

# --- Transcoding ---
echo "Transcoding into multiple representations..."
declare -a INPUT_FILES # Array to hold the paths of transcoded files

for i in "${!REPS[@]}"; do
    read -r resolution bitrate_v bitrate_a <<<"${REPS[$i]}"
    height="${resolution#*x}" # Extract height (e.g., 240 from 426x240)
    output_file="bbb_30s_${height}p.mp4"
    
    echo "Creating ${height}p representation..."
    ffmpeg -y -i "$TRIMMED_VIDEO_FILE" \
        -vf "scale=$resolution" -preset medium -tune film \
        -c:v libx264 -profile:v main -level 3.1 -b:v "$bitrate_v" -maxrate "$bitrate_v" -bufsize $((${bitrate_v%k}*2))k \
        -c:a aac -b:a "$bitrate_a" \
        "$output_file"
    
    INPUT_FILES+=("$output_file")
done

echo "Transcoding complete."

# --- DASH Packaging ---
echo "Packaging representations into DASH format using MP4Box..."
# Construct MP4Box command arguments from the INPUT_FILES array
MP4BOX_ARGS=""
for f in "${INPUT_FILES[@]}"; do
    MP4BOX_ARGS+="-add $f "
done

# Create DASH segments (e.g., 2 seconds long) and the manifest
mp4box -dash 2000 -frag 2000 -rap -segment-name 'segment_$RepresentationID$_' -out manifest.mpd $MP4BOX_ARGS

if [ ! -f "manifest.mpd" ]; then
    echo "Error: MP4Box failed to create manifest.mpd"
    cd ..
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "DASH packaging complete."

# --- Deployment ---
echo "Moving DASH files to $OUTPUT_DIR..."
sudo cp manifest.mpd *.m4s "$OUTPUT_DIR/"

# --- Permissions ---
echo "Setting permissions for web server..."
sudo chown -R www-data:www-data "$OUTPUT_DIR"
sudo chmod -R a+r "$OUTPUT_DIR" # Ensure all users can read

# --- Cleanup ---
echo "Cleaning up temporary files..."
cd ..
# rm -rf "$TEMP_DIR" # Keep temp dir for debugging if needed

echo "Video preparation finished. Files are in $OUTPUT_DIR"
echo "Manifest file: $OUTPUT_DIR/manifest.mpd"

exit 0 