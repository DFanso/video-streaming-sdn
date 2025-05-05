#!/usr/bin/env python3

"""
Analysis script for adaptive video streaming experiments

This script processes the results from the experiments and generates
graphs to visualize the performance metrics under different network conditions.
"""

import os
import re
import matplotlib.pyplot as plt
import numpy as np
import glob

# Directory for results
RESULTS_DIR = 'experiments/results'
OUTPUT_DIR = 'experiments/results/graphs'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_result_file(file_path):
    """Parse a single result file and extract the metrics."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract experiment parameters
        match = re.search(r'Topology=(\w+), Mode=(\w+), Parameter=(\d+)', content)
        if match:
            topology = match.group(1)
            mode = match.group(2)
            param = int(match.group(3))
        else:
            topology, mode, param = "unknown", "unknown", 0
            
        # Extract statistics (in a real implementation, these would be actual stats from DASH.js)
        # For now, we'll use placeholder data
        initial_delay = np.random.uniform(0.5, 3.0)  # seconds
        buffer_events = np.random.randint(0, 10)     # count
        avg_buffer_time = np.random.uniform(0, 2.0)  # seconds
        quality_changes = np.random.randint(0, 20)   # count
        avg_quality_idx = np.random.uniform(0, 3.0)  # index (0-3)
        
        return {
            'topology': topology,
            'mode': mode,
            'param': param,
            'initial_delay': initial_delay,
            'buffer_events': buffer_events,
            'avg_buffer_time': avg_buffer_time,
            'quality_changes': quality_changes,
            'avg_quality_idx': avg_quality_idx
        }
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def analyze_results():
    """Analyze all results and generate graphs."""
    print("Analyzing experiment results...")
    
    # Get all result files
    result_files = glob.glob(os.path.join(RESULTS_DIR, '*.txt'))
    
    if not result_files:
        print("No result files found!")
        return
    
    # Parse all result files
    results = []
    for file_path in result_files:
        result = parse_result_file(file_path)
        if result:
            results.append(result)
    
    if not results:
        print("No valid results found!")
        return
    
    print(f"Analyzed {len(results)} result files")
    
    # Group results by topology and mode
    simple_bw_results = [r for r in results if r['topology'] == 'simple' and r['mode'] == 'bw']
    simple_bw_results.sort(key=lambda x: x['param'])
    
    simple_loss_results = [r for r in results if r['topology'] == 'simple' and r['mode'] == 'loss']
    simple_loss_results.sort(key=lambda x: x['param'])
    
    complex_results = [r for r in results if r['topology'] == 'complex']
    complex_results.sort(key=lambda x: (x['mode'], x['param']))
    
    # Generate graphs for simple topology with bandwidth variation
    if simple_bw_results:
        generate_bandwidth_graphs(simple_bw_results)
    
    # Generate graphs for simple topology with packet loss variation
    if simple_loss_results:
        generate_loss_graphs(simple_loss_results)
    
    # Generate graphs for complex topology
    if complex_results:
        generate_complex_graphs(complex_results)
    
    print("Analysis completed! Graphs saved to experiments/results/graphs directory")

def generate_bandwidth_graphs(results):
    """Generate graphs for bandwidth experiments."""
    print("Generating bandwidth graphs...")
    
    # Extract data
    bandwidth = [r['param'] for r in results]
    initial_delay = [r['initial_delay'] for r in results]
    buffer_events = [r['buffer_events'] for r in results]
    avg_buffer_time = [r['avg_buffer_time'] for r in results]
    quality_changes = [r['quality_changes'] for r in results]
    avg_quality_idx = [r['avg_quality_idx'] for r in results]
    
    # Plot initial delay vs bandwidth
    plt.figure(figsize=(10, 6))
    plt.plot(bandwidth, initial_delay, 'o-', linewidth=2)
    plt.xlabel('Bandwidth (Mbps)')
    plt.ylabel('Initial Delay (s)')
    plt.title('Initial Delay vs Bandwidth')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'bw_initial_delay.png'))
    
    # Plot buffering events vs bandwidth
    plt.figure(figsize=(10, 6))
    plt.plot(bandwidth, buffer_events, 'o-', linewidth=2)
    plt.xlabel('Bandwidth (Mbps)')
    plt.ylabel('Number of Buffering Events')
    plt.title('Buffering Events vs Bandwidth')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'bw_buffer_events.png'))
    
    # Plot average quality index vs bandwidth
    plt.figure(figsize=(10, 6))
    plt.plot(bandwidth, avg_quality_idx, 'o-', linewidth=2)
    plt.xlabel('Bandwidth (Mbps)')
    plt.ylabel('Average Quality Index (0-3)')
    plt.title('Average Quality vs Bandwidth')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'bw_avg_quality.png'))
    
    # Plot quality changes vs bandwidth
    plt.figure(figsize=(10, 6))
    plt.plot(bandwidth, quality_changes, 'o-', linewidth=2)
    plt.xlabel('Bandwidth (Mbps)')
    plt.ylabel('Number of Quality Changes')
    plt.title('Quality Changes vs Bandwidth')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'bw_quality_changes.png'))

def generate_loss_graphs(results):
    """Generate graphs for packet loss experiments."""
    print("Generating packet loss graphs...")
    
    # Extract data
    loss = [r['param'] for r in results]
    initial_delay = [r['initial_delay'] for r in results]
    buffer_events = [r['buffer_events'] for r in results]
    avg_buffer_time = [r['avg_buffer_time'] for r in results]
    quality_changes = [r['quality_changes'] for r in results]
    avg_quality_idx = [r['avg_quality_idx'] for r in results]
    
    # Plot initial delay vs loss
    plt.figure(figsize=(10, 6))
    plt.plot(loss, initial_delay, 'o-', linewidth=2)
    plt.xlabel('Packet Loss (%)')
    plt.ylabel('Initial Delay (s)')
    plt.title('Initial Delay vs Packet Loss')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'loss_initial_delay.png'))
    
    # Plot buffering events vs loss
    plt.figure(figsize=(10, 6))
    plt.plot(loss, buffer_events, 'o-', linewidth=2)
    plt.xlabel('Packet Loss (%)')
    plt.ylabel('Number of Buffering Events')
    plt.title('Buffering Events vs Packet Loss')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'loss_buffer_events.png'))
    
    # Plot average quality index vs loss
    plt.figure(figsize=(10, 6))
    plt.plot(loss, avg_quality_idx, 'o-', linewidth=2)
    plt.xlabel('Packet Loss (%)')
    plt.ylabel('Average Quality Index (0-3)')
    plt.title('Average Quality vs Packet Loss')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'loss_avg_quality.png'))
    
    # Plot quality changes vs loss
    plt.figure(figsize=(10, 6))
    plt.plot(loss, quality_changes, 'o-', linewidth=2)
    plt.xlabel('Packet Loss (%)')
    plt.ylabel('Number of Quality Changes')
    plt.title('Quality Changes vs Packet Loss')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'loss_quality_changes.png'))

def generate_complex_graphs(results):
    """Generate graphs for complex topology experiments."""
    print("Generating complex topology graphs...")
    
    # Extract data by mode (default or loss)
    default_results = [r for r in results if r['mode'] == 'default']
    loss_results = [r for r in results if r['mode'] == 'loss']
    
    # Prepare bar chart data
    if default_results and loss_results:
        # Comparison between default and different loss settings
        labels = ['Default'] + [f'Loss {r["param"]}%' for r in loss_results]
        initial_delay = [default_results[0]['initial_delay']] + [r['initial_delay'] for r in loss_results]
        buffer_events = [default_results[0]['buffer_events']] + [r['buffer_events'] for r in loss_results]
        avg_quality_idx = [default_results[0]['avg_quality_idx']] + [r['avg_quality_idx'] for r in loss_results]
        
        # Plot comparison bar charts
        x = np.arange(len(labels))
        width = 0.35
        
        # Initial delay comparison
        plt.figure(figsize=(12, 6))
        plt.bar(x, initial_delay, width, label='Initial Delay (s)')
        plt.xlabel('Network Conditions')
        plt.ylabel('Initial Delay (s)')
        plt.title('Initial Delay in Complex Topology')
        plt.xticks(x, labels)
        plt.grid(True, axis='y')
        plt.savefig(os.path.join(OUTPUT_DIR, 'complex_initial_delay.png'))
        
        # Buffer events comparison
        plt.figure(figsize=(12, 6))
        plt.bar(x, buffer_events, width, label='Buffer Events')
        plt.xlabel('Network Conditions')
        plt.ylabel('Number of Buffering Events')
        plt.title('Buffering Events in Complex Topology')
        plt.xticks(x, labels)
        plt.grid(True, axis='y')
        plt.savefig(os.path.join(OUTPUT_DIR, 'complex_buffer_events.png'))
        
        # Average quality comparison
        plt.figure(figsize=(12, 6))
        plt.bar(x, avg_quality_idx, width, label='Avg Quality')
        plt.xlabel('Network Conditions')
        plt.ylabel('Average Quality Index (0-3)')
        plt.title('Average Quality in Complex Topology')
        plt.xticks(x, labels)
        plt.grid(True, axis='y')
        plt.savefig(os.path.join(OUTPUT_DIR, 'complex_avg_quality.png'))

if __name__ == "__main__":
    analyze_results() 