#!/usr/bin/env python3

"""
Simple Mininet topology for adaptive video streaming with SDN

This script creates a simple network topology with one server (h1),
one client (h2), and one switch connected to an OpenDaylight controller.
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import sys
import os

def simpleTopology():
    "Create a simple topology with one server, one client, and one switch"

    # Create network with remote controller (OpenDaylight)
    info('*** Creating network with remote controller\n')
    controller_ip = '127.0.0.1'  # Change this to the IP of your OpenDaylight controller
    
    net = Mininet(topo=None,
                  build=False,
                  host=CPULimitedHost,
                  link=TCLink,
                  ipBase='10.0.0.0/8')
    
    # Add remote controller
    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip=controller_ip,
                           protocol='tcp',
                           port=6653)
    
    # Add switch
    info('*** Adding switch\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    
    # Add hosts
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)  # Server
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)  # Client
    
    # Add links with configurable bandwidth
    info('*** Adding links\n')
    net.addLink(h1, s1, cls=TCLink, bw=10)  # 10 Mbps link for server to switch
    net.addLink(h2, s1, cls=TCLink, bw=5)   # 5 Mbps link for client to switch
    
    # Build network
    info('*** Starting network\n')
    net.build()
    
    # Start controller
    info('*** Starting controller\n')
    for controller in net.controllers:
        controller.start()
    
    # Start switch
    info('*** Starting switch\n')
    net.get('s1').start([c0])
    
    # Configure Apache on the server host
    info('*** Configuring server\n')
    h1.cmd('service apache2 stop || true')  # Stop any existing Apache service, ignoring errors
    h1.cmd('apache2 -k start || true')      # Start Apache in the server namespace, ignoring errors
    
    # Copy Chrome wrapper to client
    if os.path.exists('./setup/chrome-wrapper.sh'):
        h2.cmd('mkdir -p /tmp/scripts')
        with open('./setup/chrome-wrapper.sh', 'r') as f:
            script = f.read()
        with open('/tmp/chrome-wrapper.sh', 'w') as f:
            f.write(script)
        h2.cmd('cp /tmp/chrome-wrapper.sh /tmp/scripts/chrome-wrapper.sh')
        h2.cmd('chmod +x /tmp/scripts/chrome-wrapper.sh')
    
    # Information
    info('*** Running CLI\n')
    info('*** Server IP: {}\n'.format(h1.IP()))
    info('*** Client IP: {}\n'.format(h2.IP()))
    info('*** To access DASH player, open a browser in h2 and navigate to http://{}//dash/index.html\n'.format(h1.IP()))
    
    # Provide useful commands
    info('*** Useful commands:\n')
    info('   h2 /tmp/scripts/chrome-wrapper.sh http://10.0.0.1/dash/index.html &  # Start Chrome browser on client to access DASH player\n')
    info('   h1 tail -f /var/log/apache2/access.log        # View Apache access logs\n')
    info('   h2 ping h1                                    # Test connectivity\n')
    
    # Start Mininet CLI
    CLI(net)
    
    # Stop network
    info('*** Stopping network\n')
    net.stop()

def variableBandwidthTopology(bw=5):
    "Create a topology with variable bandwidth"
    
    # Create network with remote controller (OpenDaylight)
    info('*** Creating network with remote controller\n')
    controller_ip = '127.0.0.1'  # Change this to the IP of your OpenDaylight controller
    
    net = Mininet(topo=None,
                  build=False,
                  host=CPULimitedHost,
                  link=TCLink,
                  ipBase='10.0.0.0/8')
    
    # Add remote controller
    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip=controller_ip,
                           protocol='tcp',
                           port=6653)
    
    # Add switch
    info('*** Adding switch\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    
    # Add hosts
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)  # Server
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)  # Client
    
    # Add links with configurable bandwidth
    info('*** Adding links with bandwidth {} Mbps\n'.format(bw))
    net.addLink(h1, s1, cls=TCLink, bw=10)    # Server link always 10 Mbps
    net.addLink(h2, s1, cls=TCLink, bw=bw)    # Client link with variable bandwidth
    
    # Build network
    info('*** Starting network\n')
    net.build()
    
    # Start controller
    info('*** Starting controller\n')
    for controller in net.controllers:
        controller.start()
    
    # Start switch
    info('*** Starting switch\n')
    net.get('s1').start([c0])
    
    # Configure Apache on the server host
    info('*** Configuring server\n')
    h1.cmd('service apache2 stop || true')  # Stop any existing Apache service, ignoring errors
    h1.cmd('apache2 -k start || true')      # Start Apache in the server namespace, ignoring errors
    
    # Information
    info('*** Running CLI\n')
    info('*** Server IP: {}\n'.format(h1.IP()))
    info('*** Client IP: {}\n'.format(h2.IP()))
    info('*** Client bandwidth: {} Mbps\n'.format(bw))
    info('*** To access DASH player, open a browser in h2 and navigate to http://{}//dash/index.html\n'.format(h1.IP()))
    
    # Start Mininet CLI
    CLI(net)
    
    # Stop network
    info('*** Stopping network\n')
    net.stop()

def variableLossTopology(loss=0):
    "Create a topology with variable packet loss"
    
    # Create network with remote controller (OpenDaylight)
    info('*** Creating network with variable packet loss\n')
    controller_ip = '127.0.0.1'  # Change this to the IP of your OpenDaylight controller
    
    net = Mininet(topo=None,
                  build=False,
                  host=CPULimitedHost,
                  link=TCLink,
                  ipBase='10.0.0.0/8')
    
    # Add remote controller
    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip=controller_ip,
                           protocol='tcp',
                           port=6653)
    
    # Add switch
    info('*** Adding switch\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    
    # Add hosts
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)  # Server
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)  # Client
    
    # Add links with packet loss
    info('*** Adding links with {}% packet loss\n'.format(loss))
    net.addLink(h1, s1, cls=TCLink, bw=10)               # Server link always 10 Mbps
    net.addLink(h2, s1, cls=TCLink, bw=5, loss=loss)     # Client link with packet loss
    
    # Build network
    info('*** Starting network\n')
    net.build()
    
    # Start controller
    info('*** Starting controller\n')
    for controller in net.controllers:
        controller.start()
    
    # Start switch
    info('*** Starting switch\n')
    net.get('s1').start([c0])
    
    # Configure Apache on the server host
    info('*** Configuring server\n')
    h1.cmd('service apache2 stop || true')  # Stop any existing Apache service, ignoring errors
    h1.cmd('apache2 -k start || true')      # Start Apache in the server namespace, ignoring errors
    
    # Information
    info('*** Running CLI\n')
    info('*** Server IP: {}\n'.format(h1.IP()))
    info('*** Client IP: {}\n'.format(h2.IP()))
    info('*** Packet loss: {}%\n'.format(loss))
    info('*** To access DASH player, open a browser in h2 and navigate to http://{}//dash/index.html\n'.format(h1.IP()))
    
    # Start Mininet CLI
    CLI(net)
    
    # Stop network
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == 'bw' and len(sys.argv) > 2:
            # Variable bandwidth mode
            try:
                bw = float(sys.argv[2])
                variableBandwidthTopology(bw)
            except ValueError:
                print("Bandwidth must be a number")
        elif mode == 'loss' and len(sys.argv) > 2:
            # Variable packet loss mode
            try:
                loss = float(sys.argv[2])
                variableLossTopology(loss)
            except ValueError:
                print("Loss percentage must be a number")
        else:
            print("Usage: python3 simple_topology.py [bw <bandwidth>|loss <loss_percentage>]")
    else:
        # Default simple topology
        simpleTopology() 