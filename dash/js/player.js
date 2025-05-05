/**
 * Configuration for DASH.js player for adaptive video streaming over SDN
 */

(function() {
    'use strict';
    
    // Player configuration
    const playerConfig = {
        debug: {
            logLevel: dashjs.Debug.LOG_LEVEL_INFO
        },
        streaming: {
            fastSwitchEnabled: true,
            abr: {
                useDefaultABRRules: true,
                ABRStrategy: 'abrDynamic',
                bandwidthSafetyFactor: 0.9,
                useBufferOccupancyABR: true
            },
            buffer: {
                bufferToKeep: 30,
                bufferPruningInterval: 30,
                stableBufferTime: 30,
                bufferTimeAtTopQuality: 30
            }
        }
    };

    // Statistics container
    const stats = {
        switchHistory: [],
        bufferEvents: [],
        initialDelay: 0,
        totalStallDuration: 0,
        stallCount: 0,
        averageQuality: 0,
        qualityChangeCount: 0,
        lastQuality: -1
    };

    // Initialize player
    function initPlayer() {
        const url = "/videos/dash/manifest.mpd";
        const videoElement = document.querySelector("#videoPlayer");
        const player = dashjs.MediaPlayer().create();
        
        // Apply configuration
        player.updateSettings(playerConfig);
        
        // Initialize player
        player.initialize(videoElement, url, true);
        
        // UI elements for statistics
        const videoInfo = document.querySelector("#video-representation");
        const bufferLevel = document.querySelector("#buffer-level");
        const qualityIndex = document.querySelector("#quality-index");
        const maxIndex = document.querySelector("#max-index");
        const eventLog = document.querySelector("#event-log");
        const statsButton = document.querySelector("#stats-button");
        const statsOutput = document.querySelector("#stats-output");
        
        // Track initial load time
        const startTime = performance.now();
        let playbackStarted = false;
        
        // Event listeners
        player.on(dashjs.MediaPlayer.events.PLAYBACK_STARTED, function() {
            if (!playbackStarted) {
                playbackStarted = true;
                stats.initialDelay = (performance.now() - startTime) / 1000;
                logEvent("Initial delay: " + stats.initialDelay.toFixed(2) + "s");
            }
        });
        
        player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, function(e) {
            videoInfo.innerText = e.newQuality;
            qualityIndex.innerText = e.newQuality;
            
            if (stats.lastQuality !== -1 && stats.lastQuality !== e.newQuality) {
                stats.qualityChangeCount++;
                
                stats.switchHistory.push({
                    timestamp: new Date(),
                    from: stats.lastQuality,
                    to: e.newQuality
                });
            }
            
            stats.lastQuality = e.newQuality;
            logEvent("Quality changed to: " + e.newQuality);
        });
        
        player.on(dashjs.MediaPlayer.events.BUFFER_LEVEL_UPDATED, function(e) {
            bufferLevel.innerText = e.bufferLevel.toFixed(2);
        });
        
        player.on(dashjs.MediaPlayer.events.BUFFER_EMPTY, function() {
            stats.stallCount++;
            const stallStart = performance.now();
            
            stats.bufferEvents.push({
                timestamp: new Date(),
                type: "start",
                bufferLevel: player.getBufferLength()
            });
            
            logEvent("Buffer empty - stall started");
            
            const onBufferLoaded = function() {
                const stallDuration = (performance.now() - stallStart) / 1000;
                stats.totalStallDuration += stallDuration;
                
                stats.bufferEvents.push({
                    timestamp: new Date(),
                    type: "end",
                    duration: stallDuration,
                    bufferLevel: player.getBufferLength()
                });
                
                logEvent("Buffer loaded - stall ended after " + stallDuration.toFixed(2) + "s");
                player.off(dashjs.MediaPlayer.events.BUFFER_LOADED, onBufferLoaded);
            };
            
            player.on(dashjs.MediaPlayer.events.BUFFER_LOADED, onBufferLoaded);
        });
        
        player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, function() {
            maxIndex.innerText = player.getBitrateInfoListFor("video").length - 1;
            
            // Get available bitrates
            const bitrates = player.getBitrateInfoListFor("video");
            let bitrateList = "";
            
            bitrates.forEach(function(bitrate, index) {
                bitrateList += "Quality " + index + ": " + Math.round(bitrate.bitrate / 1000) + " kbps (" + 
                               bitrate.width + "x" + bitrate.height + ")<br>";
            });
            
            document.querySelector("#available-qualities").innerHTML = bitrateList;
        });
        
        // Add button to show statistics
        if (statsButton) {
            statsButton.addEventListener("click", function() {
                calculateStatistics(player);
                statsOutput.style.display = "block";
            });
        }
        
        // Log events
        function logEvent(event) {
            const timestamp = new Date().toTimeString().split(' ')[0];
            const logItem = document.createElement("div");
            logItem.innerText = timestamp + " - " + event;
            eventLog.appendChild(logItem);
            eventLog.scrollTop = eventLog.scrollHeight;
        }
        
        // Register other basic events
        const events = [
            "playbackStarted", "playbackPaused", "playbackSeeking", 
            "bufferStalled", "error"
        ];
        
        events.forEach(function(event) {
            player.on(dashjs.MediaPlayer.events[event.toUpperCase()], function() {
                logEvent(event);
            });
        });
        
        // Return player for external access
        return player;
    }
    
    // Calculate and display statistics
    function calculateStatistics(player) {
        // Calculate average quality
        let qualitySum = 0;
        let qualityCount = 0;
        
        stats.switchHistory.forEach(function(switchEvent) {
            qualitySum += switchEvent.to;
            qualityCount++;
        });
        
        stats.averageQuality = qualityCount > 0 ? qualitySum / qualityCount : stats.lastQuality;
        
        // Prepare statistics output
        const statsOutput = document.querySelector("#stats-output");
        if (statsOutput) {
            statsOutput.innerHTML = `
                <h3>Playback Statistics</h3>
                <p>Initial delay: ${stats.initialDelay.toFixed(2)} seconds</p>
                <p>Number of stalls: ${stats.stallCount}</p>
                <p>Total stall duration: ${stats.totalStallDuration.toFixed(2)} seconds</p>
                <p>Average stall duration: ${stats.stallCount > 0 ? (stats.totalStallDuration / stats.stallCount).toFixed(2) : 0} seconds</p>
                <p>Quality changes: ${stats.qualityChangeCount}</p>
                <p>Average quality index: ${stats.averageQuality.toFixed(2)}</p>
                <p>Current quality index: ${stats.lastQuality}</p>
                <p>Current buffer level: ${player.getBufferLength().toFixed(2)} seconds</p>
            `;
        }
        
        // Also log to console for data collection
        console.log("Statistics: initial_delay=" + stats.initialDelay.toFixed(2) + 
                  ",stall_count=" + stats.stallCount +
                  ",stall_duration=" + stats.totalStallDuration.toFixed(2) +
                  ",quality_changes=" + stats.qualityChangeCount +
                  ",avg_quality=" + stats.averageQuality.toFixed(2));
        
        return stats;
    }
    
    // Initialize player when DOM is loaded
    document.addEventListener("DOMContentLoaded", function() {
        const player = initPlayer();
        
        // Make player and stats accessible globally
        window.dashPlayer = player;
        window.dashStats = stats;
        window.getStats = function() {
            return calculateStatistics(player);
        };
    });
})(); 