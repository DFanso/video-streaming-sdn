#!/bin/bash

# Script to install and set up Apache server with DASH.js player
echo "Setting up Apache server and DASH.js player..."

# Install Apache
echo "Installing Apache server..."
sudo apt-get install -y apache2

# Create directory for DASH.js in Apache document root
echo "Setting up DASH.js player..."
sudo mkdir -p /var/www/html/dash/js
sudo chown -R $USER:$USER /var/www/html/dash

# Download and install DASH.js
cd /tmp
echo "Cloning DASH.js repository..."
git clone https://github.com/Dash-Industry-Forum/dash.js.git
cd dash.js

# Install Node.js dependencies and build
echo "Building DASH.js (this may take a few minutes)..."
# Create a basic package.json if it doesn't exist or is malformed
if [ ! -f package.json ] || ! grep -q "dependencies" package.json; then
    echo '{
  "name": "dashjs",
  "version": "4.0.0",
  "description": "A reference client implementation for the playback of MPEG DASH via JavaScript",
  "main": "index.js",
  "scripts": {
    "build": "grunt dist"
  },
  "dependencies": {
    "grunt": "^1.0.4",
    "grunt-cli": "^1.3.2",
    "grunt-contrib-connect": "^2.0.0",
    "grunt-contrib-copy": "^1.0.0",
    "grunt-contrib-jshint": "^2.1.0",
    "grunt-contrib-uglify": "^4.0.1",
    "grunt-contrib-watch": "^1.1.0",
    "grunt-browserify": "^5.3.0",
    "grunt-jsdoc": "^2.4.0"
  }
}' > package.json
fi

# Install dependencies and build
npm install
npm run build

# In case the build process fails, try to get the pre-built file
if [ ! -d "dist" ]; then
    echo "Build process failed, downloading pre-built files..."
    mkdir -p dist
    curl -L https://cdn.dashjs.org/latest/dash.all.min.js -o dist/dash.all.min.js
    curl -L https://cdn.dashjs.org/latest/dash.all.min.js.map -o dist/dash.all.min.js.map
    echo "/* Placeholder CSS */" > dist/dash.all.min.css
fi

# Copy DASH.js files to Apache document root
echo "Copying DASH.js files to web directory..."
mkdir -p /var/www/html/dash/js
cp -r dist/* /var/www/html/dash/js/

# Create index.html for DASH player
echo "Creating DASH player HTML page..."
cat > /var/www/html/dash/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>DASH.js Reference Player</title>
    <meta name="description" content="DASH.js Reference Player for Adaptive Video Streaming over SDN">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="js/dash.all.min.css">
    <script src="js/dash.all.min.js"></script>
</head>
<body>
    <div>
        <div class="dash-video-player">
            <div class="videoContainer">
                <video id="videoPlayer" controls></video>
            </div>
        </div>
        <div id="stats-info">
            <div id="video-info">
                <span>Video Representation: </span><span id="video-representation"></span><br/>
                <span>Buffer Level: </span><span id="buffer-level"></span><span> s</span><br/>
                <span>Quality Index: </span><span id="quality-index"></span><br/>
                <span>Max Index: </span><span id="max-index"></span><br/>
            </div>
            <div id="event-info">
                <span>Playback Events:</span><br/>
                <div id="event-log" style="height:200px; overflow:auto; border:1px solid #ccc;"></div>
            </div>
        </div>
    </div>

    <script>
        (function(){
            var url = "videos/dash/manifest.mpd";
            var player = dashjs.MediaPlayer().create();
            var videoElement = document.querySelector("#videoPlayer");
            
            player.initialize(videoElement, url, true);
            player.setAutoPlay(true);
            
            // Statistics and events
            var videoInfo = document.querySelector("#video-representation");
            var bufferLevel = document.querySelector("#buffer-level");
            var qualityIndex = document.querySelector("#quality-index");
            var maxIndex = document.querySelector("#max-index");
            var eventLog = document.querySelector("#event-log");
            
            player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, function(e) {
                videoInfo.innerText = e.newQuality;
                qualityIndex.innerText = e.newQuality;
            });
            
            player.on(dashjs.MediaPlayer.events.BUFFER_LEVEL_UPDATED, function(e) {
                bufferLevel.innerText = e.bufferLevel.toFixed(2);
            });
            
            player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, function(e) {
                maxIndex.innerText = player.getBitrateInfoListFor("video").length - 1;
            });
            
            var events = [
                "playbackStarted", "playbackPaused", "playbackSeeking", "bufferEmpty", 
                "bufferLoaded", "bufferStalled", "error"
            ];
            
            events.forEach(function(event) {
                player.on(dashjs.MediaPlayer.events[event.toUpperCase()], function(e) {
                    var timestamp = new Date().toTimeString().split(' ')[0];
                    var logItem = document.createElement("div");
                    logItem.innerText = timestamp + " - " + event;
                    eventLog.appendChild(logItem);
                    eventLog.scrollTop = eventLog.scrollHeight;
                });
            });
        })();
    </script>
</body>
</html>
EOF

# Create a directory to host video files
sudo mkdir -p /var/www/html/videos/dash
sudo chown -R $USER:$USER /var/www/html/videos

# Enable CORS for testing
sudo tee /etc/apache2/conf-available/cors.conf > /dev/null << 'EOF'
<IfModule mod_headers.c>
    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header set Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Range"
</IfModule>
EOF

sudo a2enconf cors
sudo a2enmod headers
sudo systemctl restart apache2

echo "Apache server with DASH.js player has been set up!"
echo "Access the DASH player at: http://localhost/dash/index.html" 