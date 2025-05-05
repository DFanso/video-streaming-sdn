# Adaptive Video Streaming over SDN

This project implements an adaptive video streaming testbed using DASH.js, Apache server, and Mininet with SDN integration to investigate how network conditions affect video streaming quality.

## Overview

Adaptive Video Streaming allows media to adapt to network conditions, optimizing the viewing experience. This project:
- Sets up a testbed with DASH.js, Apache server, and mininet
- Configures OpenDaylight as the SDN controller
- Investigates how network conditions affect streaming quality metrics
- Demonstrates SDN's potential for improving video streaming

## Requirements

- Ubuntu Desktop 18.04 VM
- Mininet network emulator
- OpenDaylight controller
- Apache web server
- Firefox or Chrome browser
- Python 3.x
- DASH.js player
- FFmpeg (for video segmentation)

## Project Structure

```
.
├── README.md                       # This file
├── setup/                          # Setup scripts
│   ├── install_dependencies.sh     # Script to install all dependencies
│   ├── setup_mininet.sh            # Script to install and setup mininet
│   ├── setup_opendaylight.sh       # Script to install OpenDaylight controller
│   ├── setup_apache.sh             # Script to setup Apache and DASH.js
│   └── setup_video.sh              # Script to prepare video segments
├── topology/                       # Network topology configurations
│   ├── simple_topology.py          # Simple SDN topology script
│   └── complex_topology.py         # More complex network topology
├── dash/                           # DASH.js player files
│   ├── index.html                  # Main player page
│   └── player.js                   # Player configuration
├── videos/                         # Video files
│   ├── original/                   # Original video files
│   └── dash/                       # DASH segmented videos
└── experiments/                    # Experiment scripts and results
    ├── run_experiments.sh          # Script to run all experiments
    ├── analyze_results.py          # Script to analyze experiment results
    └── results/                    # Directory for experiment results
```

## Setup Instructions

1. **VM Installation**
   ```bash
   # Install Ubuntu 18.04 Desktop VM
   # Follow the instructions at https://releases.ubuntu.com/18.04/
   ```

2. **Run the setup script**
   ```bash
   bash setup/install_dependencies.sh
   ```

3. **Prepare the network**
   ```bash
   sudo python topology/simple_topology.py
   ```

4. **Start streaming**
   Open a browser in the client mininet host and navigate to:
   ```
   http://[server-ip]/dash/index.html
   ```

## Experiments

The experiments investigate streaming quality under different network conditions:
- Different bandwidth limitations
- Various packet loss settings (0%, 1%, 5%)
- Different network topologies

## Analysis

Results are collected and analyzed for:
- Initial delay
- Average buffer level
- Number of buffering events
- Video quality changes
- Network utilization

## SDN Network Statistics

The OpenDaylight controller collects network statistics through REST API. Example queries:
- Flow statistics: `GET http://[controller-ip]:8181/restconf/operational/opendaylight-inventory:nodes/`
- Port statistics: `GET http://[controller-ip]:8181/restconf/operational/opendaylight-inventory:nodes/node/{id}/node-connector/{port}`

## License

See the LICENSE file for details.

