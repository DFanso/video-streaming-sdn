#!/bin/bash

# Main installation script for Adaptive Video Streaming over SDN
# This script runs all the required setup scripts

echo "Starting installation of all dependencies..."

# Make all scripts executable
chmod +x setup/*.sh

# Update system packages
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install common dependencies
echo "Installing common dependencies..."
sudo apt-get install -y git curl wget python3 python3-pip unzip net-tools htop

# Install Node.js (needed for DASH.js)
echo "Installing Node.js..."
curl -sL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g npm@latest

# Install specific components
echo "Setting up Mininet..."
./setup/setup_mininet.sh

echo "Setting up OpenDaylight controller..."
./setup/setup_opendaylight.sh

echo "Setting up Apache and DASH.js..."
./setup/setup_apache.sh

echo "Setting up video segments..."
./setup/setup_video.sh

echo "Installation completed successfully!"
echo "You can now run the experiments using the scripts in the 'experiments' directory."
echo "Start the simple topology with: sudo python3 topology/simple_topology.py" 