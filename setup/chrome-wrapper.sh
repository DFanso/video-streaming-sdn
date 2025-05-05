#!/bin/bash

# Chrome wrapper script that launches Chrome with --no-sandbox flag
# for use in Mininet hosts where we're running as root
# Usage: chrome-wrapper.sh [URL]

# You can adjust the path to your installed Chrome/Chromium
CHROME_PATH="google-chrome"
# Alternatively for other systems: chromium-browser, chrome, etc.

# Add proper flags to make Chrome work in a root environment
exec $CHROME_PATH --no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage "$@" 