#!/usr/bin/env python3
import os
import sys
import subprocess

# Add the project root directory to the Python path
sys.path.insert(0, os.getcwd())

def get_env_bool(name, default=False):
    """Get boolean environment variable with default."""
    value = os.environ.get(name, str(default)).lower()
    return value in ('true', '1', 'yes', 'y')

# Get environment variables with defaults
default_mode = os.environ.get('DEFAULT_MODE', 'normal')
gossip_interval = os.environ.get('GOSSIP_INTERVAL', '5.0')
disable_gossip = get_env_bool('DISABLE_GOSSIP', False)

# AIMD congestion control settings
aimd_window = os.environ.get('AIMD_WINDOW')
aimd_min_window = os.environ.get('AIMD_MIN_WINDOW')
aimd_max_window = os.environ.get('AIMD_MAX_WINDOW')

# Parallel mode settings
parallel_threads = os.environ.get('PARALLEL_THREADS')

# Execute the CLI command with all arguments passed to this script
if len(sys.argv) > 1:
    args = sys.argv[1:]
else:
    # Use environment variables for default configuration
    args = ["src/cli.py", "--host", "0.0.0.0", 
            "--mode", default_mode, 
            "--gossip-interval", gossip_interval]
    
    # Add no-gossip flag if gossip is disabled
    if disable_gossip:
        args.append("--no-gossip")
    
    # Build custom arguments based on the chosen mode
    if default_mode == "aimd" and (aimd_window or aimd_min_window or aimd_max_window):
        # We'll use these env vars in the congestion config command once the CLI is running
        print(f"AIMD settings from environment: window={aimd_window}KB, "
              f"min_window={aimd_min_window}KB, max_window={aimd_max_window}KB")
    
    if default_mode == "parallel" and parallel_threads:
        print(f"Parallel mode will use {parallel_threads} threads by default")

print(f"Starting PeerCrypt with args: {' '.join(args)}")
cmd = ["python"] + args
sys.exit(subprocess.call(cmd)) 