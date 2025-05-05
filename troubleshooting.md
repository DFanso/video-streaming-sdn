# Troubleshooting Guide

This document provides solutions for common issues you might encounter when setting up and running the Adaptive Video Streaming over SDN project.

## Installation Issues

### Python Package Installation Errors

If you encounter errors related to Python packages:

```
E: Unable to locate package python-matplotlib
E: Unable to locate package python-numpy
E: Package 'python-pip' has no installation candidate
```

This indicates that the script is trying to install Python 2 packages which may not be available in newer Ubuntu distributions. The scripts have been updated to use Python 3 packages instead.

**Solution**: Make sure you're using the latest version of the setup scripts, which use Python 3 packages. You can manually install the required packages with:

```bash
sudo apt-get install -y python3-matplotlib python3-numpy python3-pip
```

### OpenVSwitch Controller Issues

If you see errors like:

```
Failed to stop openvswitch-controller.service: Unit openvswitch-controller.service not loaded.
update-rc.d: error: cannot find a LSB script for openvswitch-controller
```

This happens because newer versions of Mininet use different package names.

**Solution**: This error can be safely ignored since the script has been updated to use the correct package names.

### Mininet Git Clone Issues

If you encounter issues cloning the Mininet repository with errors like:

```
Cloning into 'mininet'...
fatal: unable to connect to github.com
```

This is likely due to network restrictions or firewall settings blocking the git protocol.

**Solution**: The script has been updated to use HTTPS instead of the git protocol. If you're still having issues, you can manually clone using:

```bash
git clone https://github.com/mininet/mininet.git
```

### Chrome/Karma Test Issues

If you encounter errors related to ChromeHeadless during DASH.js installation:

```
ERROR [launcher]: No binary for ChromeHeadless browser on your platform.
Please, set "CHROME_BIN" env variable.
```

This happens because Karma is trying to run tests in a headless Chrome browser, but Chrome is not installed or the environment variable is not set.

**Solution**: The setup script has been updated to install Chrome and set the environment variable. If you're still encountering issues, you can:

1. Install Chrome manually:
```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

2. Set the CHROME_BIN environment variable:
```bash
export CHROME_BIN=$(which google-chrome)
```

3. If running in a container or CI environment, you may need to run Chrome with the --no-sandbox flag:
```bash
# In karma.conf.js
browsers: ['ChromeHeadless'],
customLaunchers: {
  ChromeHeadless: {
    base: 'Chrome',
    flags: ['--headless', '--disable-gpu', '--no-sandbox']
  }
}
```

### Chrome Sandbox Issues

If you encounter this specific error when running Chrome in headless mode:

```
Running as root without --no-sandbox is not supported. See https://crbug.com/638180
```

This happens when trying to run Chrome as the root user, which is a common scenario in Docker containers or CI environments.

**Solution**: You need to configure Chrome to run with the `--no-sandbox` flag, which has security implications but is often necessary in containerized environments:

1. Create a custom launcher in your karma.conf.js:
```javascript
module.exports = function(config) {
  config.set({
    browsers: ['ChromeHeadlessNoSandbox'],
    customLaunchers: {
      ChromeHeadlessNoSandbox: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-gpu',
          '--disable-dev-shm-usage',
          '--disable-setuid-sandbox'
        ]
      }
    }
  });
};
```

2. For other applications using Chrome, pass these flags directly to Chrome:
```bash
google-chrome --no-sandbox --disable-gpu
```

3. In containerized environments, consider running the process as a non-root user if possible.

### Node.js and DASH.js Build Issues

If you encounter issues with building DASH.js:

```
npm not found
Error while building DASH.js
```

**Solution**: Make sure Node.js and npm are installed:

```bash
curl -sL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g npm@latest
```

## Network and Topology Issues

### Apache Not Starting in Mininet

If the Apache server doesn't start correctly in the Mininet environment:

**Solution**: Check if Apache is already running on your host system, which might conflict with the Mininet instance. Stop it with:

```bash
sudo service apache2 stop
```

### Controller Connection Issues

If the switch can't connect to the OpenDaylight controller:

**Solution**: 
1. Make sure the OpenDaylight controller is running: `~/opendaylight/start-odl.sh`
2. Verify the controller IP is correct in the topology script
3. Check if the specified port (6653) is open with: `sudo netstat -tunlp | grep 6653`

### Browser Not Loading DASH.js Player

If the browser in the Mininet host doesn't load the DASH.js player:

**Solution**:
1. Check if Apache is running with: `h1 service apache2 status`
2. Verify connectivity between hosts with: `h2 ping h1`
3. Try accessing a simple HTML file to confirm Apache is serving files properly

## Experiment Issues

### Firefox Not Starting in Mininet

If Firefox doesn't start in the Mininet environment:

**Solution**: 
1. Make sure Firefox is installed: `sudo apt-get install -y firefox`
2. Check if the X server is running (required for GUI applications)
3. Try using a headless browser or curl to test without a GUI

### FFmpeg Video Encoding Errors

If you encounter errors while encoding video segments:

**Solution**:
1. Verify FFmpeg is installed: `ffmpeg -version`
2. Check if you have enough disk space: `df -h`
3. Make sure you have the required codecs: `sudo apt-get install -y ffmpeg libx264-dev`

## Common Commands

Here are some useful commands for debugging:

```bash
# Check if Python 3 is installed
python3 --version

# Verify Mininet installation
sudo mn --version

# Check OpenDaylight status
curl -u admin:admin http://localhost:8181/restconf/operational/opendaylight-inventory:nodes/

# Test Mininet connectivity
sudo mn --test pingall

# Clean up any existing Mininet processes
sudo mn -c

# Check if Apache is running
service apache2 status

# View Apache error logs
tail -f /var/log/apache2/error.log
```

## Getting Help

If you continue to experience issues after trying these solutions, you can:

1. Check the official Mininet documentation: http://mininet.org/
2. Check the official OpenDaylight documentation: https://docs.opendaylight.org/
3. Check the official DASH.js documentation: https://github.com/Dash-Industry-Forum/dash.js/wiki
4. Open an issue in the project repository with detailed error information 