#!/bin/bash

# Script to download and prepare video segments for DASH
echo "Setting up video segments for DASH..."

# Install FFmpeg
echo "Installing FFmpeg..."
sudo apt-get install -y ffmpeg

# Create directories for videos
mkdir -p videos/original
mkdir -p videos/dash

# Download Big Buck Bunny sample video
echo "Downloading sample video..."
cd videos/original
wget -c https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4 -O BigBuckBunny.mp4
cd ../..

# Create different video representations
echo "Creating video representations..."
mkdir -p videos/dash/output

# Parameters for different representations
resolutions=("320x180" "640x360" "960x540" "1280x720")
bitrates=("400k" "800k" "1200k" "2400k")

for i in {0..3}; do
    echo "Creating representation ${i}: Resolution ${resolutions[$i]}, Bitrate ${bitrates[$i]}"
    ffmpeg -i videos/original/BigBuckBunny.mp4 -c:v libx264 -b:v ${bitrates[$i]} -maxrate ${bitrates[$i]} \
           -bufsize $((${bitrates[$i]%k} * 2))k -vf "scale=${resolutions[$i]}" -c:a aac -b:a 128k \
           -f mp4 videos/dash/output/bbb_${i}.mp4
done

# Create DASH segments
echo "Creating DASH segments..."
cd videos/dash
ffmpeg -i output/bbb_0.mp4 -i output/bbb_1.mp4 -i output/bbb_2.mp4 -i output/bbb_3.mp4 \
       -map 0:v -map 0:a -map 1:v -map 1:a -map 2:v -map 2:a -map 3:v -map 3:a \
       -c:v copy -c:a copy \
       -b:v:0 400k -b:v:1 800k -b:v:2 1200k -b:v:3 2400k \
       -use_timeline 1 -use_template 1 -window_size 5 -adaptation_sets "id=0,streams=v id=1,streams=a" \
       -f dash manifest.mpd

cd ../..

# Copy DASH segments to Apache directory
echo "Copying DASH segments to Apache server..."
sudo cp -r videos/dash/* /var/www/html/videos/dash/
sudo chown -R www-data:www-data /var/www/html/videos/dash/

echo "Video segments preparation completed!"
echo "The DASH manifest is available at: http://localhost/videos/dash/manifest.mpd" 