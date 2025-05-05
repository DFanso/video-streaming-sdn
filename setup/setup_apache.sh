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

# Install Google Chrome for headless testing
echo "Installing Google Chrome for headless testing..."
if ! command -v google-chrome &> /dev/null; then
    # Add Chrome repository and install Chrome
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
fi

# Create Chrome wrapper script to force the --no-sandbox flag
echo "Creating Chrome wrapper script..."
cat > /tmp/chrome-wrapper.sh << 'EOF'
#!/bin/bash
exec google-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu "$@"
EOF
chmod +x /tmp/chrome-wrapper.sh

# Set Chrome environment variable to use our wrapper
export CHROME_BIN=/tmp/chrome-wrapper.sh
echo "Chrome wrapper location: $CHROME_BIN"

# Download and install DASH.js pre-built files
cd /tmp
echo "Downloading DASH.js pre-built files..."
mkdir -p dash.js/dist
curl -L https://cdn.dashjs.org/latest/dash.all.min.js -o dash.js/dist/dash.all.min.js
curl -L https://cdn.dashjs.org/latest/dash.all.min.js.map -o dash.js/dist/dash.all.min.js.map
echo "/* Placeholder CSS */" > dash.js/dist/dash.all.min.css

# Copy DASH.js files to Apache document root
echo "Copying DASH.js files to web directory..."
mkdir -p /var/www/html/dash/js

# Copy files from the downloaded 'dist' directory
cp -r dash.js/dist/* /var/www/html/dash/js/

# Ensure files are present, fallback to CDN download directly into web dir if necessary
if [ ! -f "/var/www/html/dash/js/dash.all.min.js" ]; then
    echo "Files not copied correctly, downloading directly to web directory from CDN..."
    curl -L https://cdn.dashjs.org/latest/dash.all.min.js -o /var/www/html/dash/js/dash.all.min.js
    curl -L https://cdn.dashjs.org/latest/dash.all.min.js.map -o /var/www/html/dash/js/dash.all.min.js.map
    # Create a minimal CSS file if needed
    if [ ! -f "/var/www/html/dash/js/dash.all.min.css" ]; then
        echo "/* Placeholder CSS */" > /var/www/html/dash/js/dash.all.min.css
    fi
fi

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
sudo systemctl restart apache2 || true

echo "Apache server with DASH.js player has been set up!"
echo "Access the DASH player at: http://localhost/dash/index.html" 