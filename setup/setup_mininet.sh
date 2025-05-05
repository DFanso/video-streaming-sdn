#!/bin/bash

# Script to install and set up Mininet
echo "Installing Mininet..."

# Install dependencies
sudo apt-get install -y mininet openvswitch-switch

# Install additional tools for mininet (using Python 3 packages)
sudo apt-get install -y python3-matplotlib python3-numpy python3-pip tcpdump wireshark

# No need to stop non-existent controller
# The following lines are commented out because they cause errors
# sudo service openvswitch-controller stop
# sudo update-rc.d openvswitch-controller disable

# Clone Mininet repository for latest version
cd /tmp
git clone git://github.com/mininet/mininet
cd mininet
git checkout -b 2.3.0 2.3.0

# Install Mininet with OpenFlow
./util/install.sh -nfv

# Return to original directory
cd -

echo "Mininet installation completed!"

# Test if Mininet works
echo "Testing Mininet installation..."
sudo mn --test pingall
if [ $? -eq 0 ]; then
    echo "Mininet test completed successfully!"
else
    echo "Mininet test failed. Please check the installation."
fi

# Clean up any Mininet instances
sudo mn -c 