#!/usr/bin/env python

"""
Complex Mininet topology for adaptive video streaming with SDN

This script creates a more complex network topology with multiple servers,
clients, and switches connected to an OpenDaylight controller.
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

def complexTopology():
    "Create a complex topology with multiple servers, clients, and switches"

    # Create network with remote controller (OpenDaylight)
    info('*** Creating complex network with remote controller\n')
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
    
    # Add switches
    info('*** Adding switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    
    # Add hosts
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)  # Server
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)  # Client 1
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)  # Client 2
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)  # Client 3
    
    # Add links with configurable bandwidth
    info('*** Adding links\n')
    # Server to switch links
    net.addLink(h1, s1, cls=TCLink, bw=100)  # 100 Mbps link for server to core switch
    
    # Core switch to edge switches
    net.addLink(s1, s2, cls=TCLink, bw=50)   # 50 Mbps link between switches
    net.addLink(s1, s3, cls=TCLink, bw=50)   # 50 Mbps link between switches
    
    # Edge switches to clients
    net.addLink(s2, h2, cls=TCLink, bw=10)   # 10 Mbps link for client 1
    net.addLink(s2, h3, cls=TCLink, bw=5)    # 5 Mbps link for client 2
    net.addLink(s3, h4, cls=TCLink, bw=2)    # 2 Mbps link for client 3
    
    # Build network
    info('*** Starting network\n')
    net.build()
    
    # Start controller
    info('*** Starting controller\n')
    for controller in net.controllers:
        controller.start()
    
    # Start switches
    info('*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    
    # Configure Apache on the server host
    info('*** Configuring server\n')
    h1.cmd('service apache2 stop')  # Stop any existing Apache service
    h1.cmd('apache2 -k start')      # Start Apache in the server namespace
    
    # Information
    info('*** Running CLI\n')
    info('*** Server IP: {}\n'.format(h1.IP()))
    info('*** Client 1 IP: {} (10 Mbps)\n'.format(h2.IP()))
    info('*** Client 2 IP: {} (5 Mbps)\n'.format(h3.IP()))
    info('*** Client 3 IP: {} (2 Mbps)\n'.format(h4.IP()))
    info('*** To access DASH player, open a browser in any client and navigate to http://{}//dash/index.html\n'.format(h1.IP()))
    
    # Start Mininet CLI
    CLI(net)
    
    # Stop network
    info('*** Stopping network\n')
    net.stop()

def complexTopologyWithLoss(loss1=0, loss2=0, loss3=0):
    "Create a complex topology with multiple clients and variable packet loss"
    
    # Create network with remote controller (OpenDaylight)
    info('*** Creating complex network with remote controller and variable packet loss\n')
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
    
    # Add switches
    info('*** Adding switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    
    # Add hosts
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)  # Server
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)  # Client 1
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)  # Client 2
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)  # Client 3
    
    # Add links with configurable bandwidth and packet loss
    info('*** Adding links with packet loss\n')
    # Server to switch links
    net.addLink(h1, s1, cls=TCLink, bw=100)  # 100 Mbps link for server to core switch
    
    # Core switch to edge switches
    net.addLink(s1, s2, cls=TCLink, bw=50)   # 50 Mbps link between switches
    net.addLink(s1, s3, cls=TCLink, bw=50)   # 50 Mbps link between switches
    
    # Edge switches to clients with different loss rates
    net.addLink(s2, h2, cls=TCLink, bw=10, loss=loss1)   # Client 1 with variable loss
    net.addLink(s2, h3, cls=TCLink, bw=5, loss=loss2)    # Client 2 with variable loss
    net.addLink(s3, h4, cls=TCLink, bw=2, loss=loss3)    # Client 3 with variable loss
    
    # Build network
    info('*** Starting network\n')
    net.build()
    
    # Start controller
    info('*** Starting controller\n')
    for controller in net.controllers:
        controller.start()
    
    # Start switches
    info('*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    
    # Configure Apache on the server host
    info('*** Configuring server\n')
    h1.cmd('service apache2 stop')  # Stop any existing Apache service
    h1.cmd('apache2 -k start')      # Start Apache in the server namespace
    
    # Information
    info('*** Running CLI\n')
    info('*** Server IP: {}\n'.format(h1.IP()))
    info('*** Client 1 IP: {} (10 Mbps, {}% loss)\n'.format(h2.IP(), loss1))
    info('*** Client 2 IP: {} (5 Mbps, {}% loss)\n'.format(h3.IP(), loss2))
    info('*** Client 3 IP: {} (2 Mbps, {}% loss)\n'.format(h4.IP(), loss3))
    info('*** To access DASH player, open a browser in any client and navigate to http://{}//dash/index.html\n'.format(h1.IP()))
    
    # Start Mininet CLI
    CLI(net)
    
    # Stop network
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'loss' and len(sys.argv) > 4:
            # Variable loss mode for all clients
            try:
                loss1 = float(sys.argv[2])
                loss2 = float(sys.argv[3])
                loss3 = float(sys.argv[4])
                complexTopologyWithLoss(loss1, loss2, loss3)
            except ValueError:
                print("Loss percentages must be numbers")
        else:
            print("Usage: python complex_topology.py [loss <loss1%> <loss2%> <loss3%>]")
    else:
        # Default complex topology
        complexTopology() 