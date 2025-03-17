#!/usr/bin/env python3
import subprocess
import os
import matplotlib.pyplot as plt
import numpy as np
import re

def run_and_plot(exec_name, start_range, end_range):
    print(f"Benchmarking: {exec_name}")
    
    # Initialize data structures for different metrics
    N_list = []
    serial_metrics = {
        'real_time': [],
        'cpu_time': [],
        'cycles': []
    }
    parallel_metrics = {
        2: {'real_time': [], 'cpu_time': [], 'cycles': []},
        4: {'real_time': [], 'cpu_time': [], 'cycles': []}
    }
    
    for i in range(start_range, end_range):
        N = i
        N_list.append(N)
        
        # Run serial version
        my_env = os.environ.copy()
        my_env["ONLY_SERIAL"] = "true"
        if "ONLY_PARALLEL" in my_env:
            del my_env["ONLY_PARALLEL"]
        result = subprocess.run([exec_name, str(N)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env)
        output_serial = result.stdout.decode('utf-8')
        
        # Process serial metrics
        for line in output_serial.splitlines():
            if "serial" in line:
                if match := re.search(r"elapsed_real_time: ([\d.]+) s", line):
                    serial_metrics['real_time'].append(float(match.group(1)))
                if match := re.search(r"elapsed_cpu_time: ([\d.]+) s", line):
                    serial_metrics['cpu_time'].append(float(match.group(1)))
                if match := re.search(r"cycles: ([\d.]+)", line):
                    serial_metrics['cycles'].append(float(match.group(1)))
        
        # Run parallel versions with different thread counts
        for n_threads in [2, 4]:
            my_env = os.environ.copy()
            my_env["OMP_NUM_THREADS"] = str(n_threads)
            my_env["ONLY_PARALLEL"] = "true"
            if "ONLY_SERIAL" in my_env:
                del my_env["ONLY_SERIAL"]
            
            result = subprocess.run([exec_name, str(N)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env)
            output = result.stdout.decode('utf-8')
            
            # Process parallel metrics
            for line in output.splitlines():
                if "parallel" in line:
                    if match := re.search(r"elapsed_real_time: ([\d.]+) s", line):
                        parallel_metrics[n_threads]['real_time'].append(float(match.group(1)))
                    if match := re.search(r"elapsed_cpu_time: ([\d.]+) s", line):
                        parallel_metrics[n_threads]['cpu_time'].append(float(match.group(1)))
                    if match := re.search(r"cycles: ([\d.]+)", line):
                        parallel_metrics[n_threads]['cycles'].append(float(match.group(1)))
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    
    # Plot 1: Cycle count comparison
    ax1.plot(N_list, serial_metrics['cycles'], 'b-', label='Serial', marker='o')
    ax1.plot(N_list, parallel_metrics[2]['cycles'], 'r-', label='Parallel (2 threads)', marker='s')
    ax1.plot(N_list, parallel_metrics[4]['cycles'], 'g-', label='Parallel (4 threads)', marker='^')
    
    ax1.set_title(f'Cycle Count Comparison - {exec_name}')
    ax1.set_xlabel('Input Size (2^N)')
    ax1.set_ylabel('Cycles')
    ax1.set_yscale('log')
    ax1.grid(True)
    ax1.legend()
    
    # Plot 2: Time comparison
    ax2.plot(N_list, serial_metrics['real_time'], 'b-', label='Serial (Real Time)', marker='o')
    ax2.plot(N_list, serial_metrics['cpu_time'], 'b--', label='Serial (CPU Time)', marker='o')
    ax2.plot(N_list, parallel_metrics[2]['real_time'], 'r-', label='Parallel 2T (Real Time)', marker='s')
    ax2.plot(N_list, parallel_metrics[2]['cpu_time'], 'r--', label='Parallel 2T (CPU Time)', marker='s')
    ax2.plot(N_list, parallel_metrics[4]['real_time'], 'g-', label='Parallel 4T (Real Time)', marker='^')
    ax2.plot(N_list, parallel_metrics[4]['cpu_time'], 'g--', label='Parallel 4T (CPU Time)', marker='^')
    
    ax2.set_title(f'Time Comparison - {exec_name}')
    ax2.set_xlabel('Input Size (2^N)')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_yscale('log')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    # Save plot
    plt.savefig(f"{exec_name.replace('./', '').replace('.run', '')}_performance.png")
    plt.close()

def main():
    # Test parameters for each sorting algorithm
    algorithms = [
        ("./bubble.run", 2, 12),
        ("./mergesort.run", 6, 18),
        ("./odd-even.run", 6, 12)
    ]
    
    for algo, start, end in algorithms:
        run_and_plot(algo, start, end)

if __name__ == "__main__":
    main()