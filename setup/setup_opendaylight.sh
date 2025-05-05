#!/bin/bash

# Script to install and set up OpenDaylight controller
echo "Setting up OpenDaylight controller..."

# Install Java 8
echo "Installing Java 8..."
sudo apt-get install -y openjdk-8-jdk
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc
source ~/.bashrc

# Create directory for OpenDaylight
mkdir -p ~/opendaylight
cd ~/opendaylight

# Download OpenDaylight (Oxygen release)
echo "Downloading OpenDaylight..."
wget https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/0.8.4/karaf-0.8.4.zip
unzip karaf-0.8.4.zip
mv karaf-0.8.4 odl

# Create start script for OpenDaylight
echo "Creating startup script..."
cat > ~/opendaylight/start-odl.sh << 'EOF'
#!/bin/bash
cd ~/opendaylight/odl
./bin/karaf
EOF

chmod +x ~/opendaylight/start-odl.sh

# Create script for installing required features
cat > ~/opendaylight/install-features.sh << 'EOF'
#!/bin/bash
cd ~/opendaylight/odl
./bin/karaf

# Once in Karaf console, install required features:
# feature:install odl-restconf odl-l2switch-switch odl-mdsal-apidocs odl-dlux-core odl-dluxapps-applications
EOF

chmod +x ~/opendaylight/install-features.sh

echo "OpenDaylight installation completed!"
echo "To start OpenDaylight, run: ~/opendaylight/start-odl.sh"
echo "Once in the Karaf console, install the required features with:"
echo "feature:install odl-restconf odl-l2switch-switch odl-mdsal-apidocs odl-dlux-core odl-dluxapps-applications"
echo "Access the OpenDaylight web interface at: http://localhost:8181/index.html"
echo "Default credentials: admin/admin"

cd - 