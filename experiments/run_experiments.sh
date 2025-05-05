#!/bin/bash

# Script to run experiments with different network conditions
echo "Running adaptive video streaming experiments..."

# Create results directory if it doesn't exist
mkdir -p experiments/results

# Function to run a single experiment
run_experiment() {
    topology=$1
    mode=$2
    param=$3
    result_file="experiments/results/${topology}_${mode}_${param}.txt"
    
    echo "Running experiment: Topology=${topology}, Mode=${mode}, Parameter=${param}"
    echo "Results will be saved to: ${result_file}"
    
    # Start the topology
    if [ "$topology" == "simple" ]; then
        if [ "$mode" == "bw" ]; then
            sudo python3 topology/simple_topology.py bw $param &
        elif [ "$mode" == "loss" ]; then
            sudo python3 topology/simple_topology.py loss $param &
        else
            sudo python3 topology/simple_topology.py &
        fi
        topo_pid=$!
    else
        if [ "$mode" == "loss" ]; then
            sudo python3 topology/complex_topology.py loss $param $param $param &
        else
            sudo python3 topology/complex_topology.py &
        fi
        topo_pid=$!
    fi
    
    # Wait for the topology to initialize
    sleep 10
    
    # Get the server IP (h1)
    server_ip=$(sudo mn -c && sudo python3 -c "from mininet.net import Mininet; from mininet.node import Controller, RemoteController; from mininet.cli import CLI; from mininet.log import setLogLevel; setLogLevel('info'); net = Mininet(); h1 = net.addHost('h1'); print(h1.IP())")
    
    # Start Firefox on client (h2) and access the DASH player
    sudo mn -x h2 firefox http://${server_ip}/dash/index.html &
    firefox_pid=$!
    
    # Let the video play for a set amount of time
    echo "Letting the video play for 60 seconds..."
    sleep 60
    
    # Capture statistics from the DASH player using a JavaScript snippet
    # This would ideally be integrated into the DASH.js player to export stats
    echo "Collecting statistics..."
    stats=$(sudo mn -x h2 "curl -s 'http://${server_ip}/dash/index.html' | grep -o 'Statistics: .*'")
    
    # Save the results
    echo "Experiment: Topology=${topology}, Mode=${mode}, Parameter=${param}" > $result_file
    echo "Date: $(date)" >> $result_file
    echo "Server IP: ${server_ip}" >> $result_file
    echo "Statistics: ${stats}" >> $result_file
    
    # Cleanup
    kill $firefox_pid
    kill $topo_pid
    sudo mn -c
    
    echo "Experiment completed!"
    sleep 5
}

# Simple topology experiments
echo "Running simple topology experiments..."

# Bandwidth experiments
echo "Running bandwidth experiments..."
run_experiment "simple" "bw" "10"  # 10 Mbps
run_experiment "simple" "bw" "5"   # 5 Mbps
run_experiment "simple" "bw" "2"   # 2 Mbps
run_experiment "simple" "bw" "1"   # 1 Mbps

# Packet loss experiments
echo "Running packet loss experiments..."
run_experiment "simple" "loss" "0"   # 0% packet loss
run_experiment "simple" "loss" "1"   # 1% packet loss
run_experiment "simple" "loss" "5"   # 5% packet loss

# Complex topology experiments
echo "Running complex topology experiments..."
run_experiment "complex" "default" "0"  # Default settings
run_experiment "complex" "loss" "1"     # 1% packet loss
run_experiment "complex" "loss" "5"     # 5% packet loss

echo "All experiments completed!"
echo "Results are available in the experiments/results directory."

# Analyze the results
echo "Analyzing results..."
python3 experiments/analyze_results.py 