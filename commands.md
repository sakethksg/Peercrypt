# PeerCrypt Commands Reference

This document provides a comprehensive reference for all PeerCrypt commands and options. Use these commands in the interactive CLI after starting the application.

## Table of Contents

- [Basic Commands](#basic-commands)
- [Network and Peer Management](#network-and-peer-management)
- [File Transfer Commands](#file-transfer-commands)
- [Transfer Mode Options](#transfer-mode-options)
  - [Normal Mode](#normal-mode)
  - [Token Bucket Mode](#token-bucket-mode)
  - [AIMD Mode](#aimd-mode-congestion-control)
  - [QoS Mode](#qos-mode-quality-of-service)
  - [Parallel Mode](#parallel-mode)
  - [Multicast Mode](#multicast-mode)
- [Congestion Control Configuration](#congestion-control-configuration)
- [Command Combinations](#command-combinations)

## Basic Commands

```bash
help                      # Show available commands and current status
status                    # Show current mode and configuration
set-mode <mode>           # Change transfer mode (normal|token-bucket|aimd|qos|parallel|multicast)
quit or exit              # Exit the application
```

## Network and Peer Management

```bash
# Peer discovery and management
list-peers                # Show discovered peers and reliability scores
join <host> <port>        # Join an existing network through a peer
health-check <host> <port> # Check if a peer is reachable
reconnect <host> <port>   # Attempt to reconnect to a problematic peer

# Gossip configuration
gossip on                 # Enable gossip-based peer discovery
gossip off                # Disable gossip-based peer discovery
gossip interval <seconds> # Set gossip interval in seconds (e.g., gossip interval 10)
```

## File Transfer Commands

### Basic Send and Receive

```bash
# Basic file transfer syntax
send <file> <host> <port> [options]   # Send a file to a specific host
receive                               # Start receiving a file
multicast-receive [port-range]        # Start multicast receiver (also: mreceive)
```

Example:
```bash
send myfile.txt 192.168.154.128 5000  # Send file using current transfer mode
receive                               # Start receiving on default port
multicast-receive 5000-5010           # Listen for multicast on ports 5000-5010
```

## Transfer Mode Options

### Normal Mode

The default transfer mode with basic encryption and no additional options.

```bash
# Usage
send <file> <host> <port>

# Example
send myfile.txt 192.168.154.128 5000  # Send using normal mode
```

### Token Bucket Mode

Rate-limited transfers to ensure consistent bandwidth usage and prevent network flooding.

```bash
# Syntax
send <file> <host> <port> -b <bucket_size> -r <rate>

# Parameters
# -b, --bucket-size: Maximum burst size in bytes
# -r, --rate: Average transfer rate in bytes/second

# Examples
send myfile.txt 192.168.154.128 5000 -b 1024 -r 100  # 1KB bucket, 100 bytes/sec
send myfile.txt 192.168.154.128 5000 -b 2048 -r 200  # 2KB bucket, 200 bytes/sec
send myfile.txt 192.168.154.128 5000 -b 4096 -r 500  # 4KB bucket, 500 bytes/sec
```

### AIMD Mode (Congestion Control)

Adaptive congestion control that dynamically adjusts to network conditions.

```bash
# Basic syntax
send <file> <host> <port> [window options] [detection options]

# Window size options
# -w, --window: Initial congestion window size in KB
# -min-w, --min-window: Minimum window size in KB
# -max-w, --max-window: Maximum window size in KB

# Detection mechanism options
# -no-timeout: Disable timeout-based congestion detection
# -no-dupack: Disable duplicate ACK-based congestion detection
# -ack-threshold <num>: Set duplicate ACK threshold (default: 3)

# Window size examples
send myfile.txt 192.168.154.128 5000 -w 4                           # 4KB window
send myfile.txt 192.168.154.128 5000 -w 8 -min-w 2 -max-w 32        # 8KB window, min 2KB, max 32KB
send myfile.txt 192.168.154.128 5000 -w 12 -min-w 3 -max-w 48       # 12KB window, min 3KB, max 48KB
send myfile.txt 192.168.154.128 5000 -w 16 -min-w 4 -max-w 64       # 16KB window, min 4KB, max 64KB
send myfile.txt 192.168.154.128 5000 -w 24 -min-w 6 -max-w 96       # 24KB window, min 6KB, max 96KB

# Detection mechanism examples
send myfile.txt 192.168.154.128 5000 -w 16 -no-timeout              # Disable timeout detection
send myfile.txt 192.168.154.128 5000 -w 8 -no-dupack                # Disable duplicate ACK detection
send myfile.txt 192.168.154.128 5000 -w 8 -ack-threshold 3          # Set duplicate ACK threshold to 3

# Combined options
send myfile.txt 192.168.154.128 5000 -w 8 -no-timeout -ack-threshold 3
send myfile.txt 192.168.154.128 5000 -w 16 -ack-threshold 2
send myfile.txt 192.168.154.128 5000 -w 8 -no-timeout -no-dupack
send myfile.txt 192.168.154.128 5000 -w 8 -min-w 2 -max-w 32 -ack-threshold 3
send myfile.txt 192.168.154.128 5000 -w 16 -min-w 4 -max-w 64 -no-timeout -ack-threshold 4
send myfile.txt 192.168.154.128 5000 -w 12 -min-w 3 -max-w 48 -no-dupack
```

### QoS Mode (Quality of Service)

Priority-based transfers to ensure important files get transferred with higher priority.

```bash
# Syntax
send <file> <host> <port> -p <priority>

# Parameters
# -p, --priority: Transfer priority level (low|normal|high)

# Priority levels (bandwidth allocation)
send myfile.txt 192.168.154.128 5000 -p low      # Low priority (receives ~20% of bandwidth)
send myfile.txt 192.168.154.128 5000 -p normal   # Normal priority (receives ~30% of bandwidth)
send myfile.txt 192.168.154.128 5000 -p high     # High priority (receives ~50% of bandwidth)
```

### Parallel Mode

Multi-threaded transfers to maximize throughput on high-bandwidth networks.

```bash
# Syntax
send <file> <host> <port> -t <threads>

# Parameters
# -t, --threads: Number of parallel threads for the transfer

# Thread count examples
send myfile.txt 192.168.154.128 5000 -t 2        # 2 threads (for low-bandwidth networks)
send myfile.txt 192.168.154.128 5000 -t 4        # 4 threads (default, balanced performance)
send myfile.txt 192.168.154.128 5000 -t 8        # 8 threads (for high-bandwidth networks)
```

### Multicast Mode

Send files to multiple receivers simultaneously.

```bash
# Basic multicast (interactive mode that prompts for additional targets)
send <file> <host> <port> -m

# Dual-target mode (sends to exactly two targets)
send <file> <host> <port> -dual

# Examples
send myfile.txt 192.168.154.128 5000 -m          # Interactive multicast mode
send myfile.txt 192.168.154.128 5000 -dual       # Send to exactly two targets
```

## Congestion Control Configuration

Runtime configuration for AIMD congestion control parameters.

```bash
# Window size configuration
congestion window <size>            # Set initial window size in KB
congestion min-window <size>        # Set minimum window size in KB
congestion max-window <size>        # Set maximum window size in KB

# Detection mechanism configuration
congestion timeout on|off           # Enable/disable timeout-based detection
congestion dupack on|off            # Enable/disable duplicate ACK detection
congestion threshold <number>       # Set duplicate ACK threshold (default: 3)

# Window size examples
congestion window 4                 # Small window (conservative, high packet loss)
congestion window 8                 # Medium window (balanced)
congestion window 16                # Large window (aggressive, stable network)
congestion min-window 1             # Very small minimum window (conservative)
congestion min-window 2             # Standard minimum window
congestion max-window 16            # Small maximum window (conservative)
congestion max-window 32            # Medium maximum window (balanced)
congestion max-window 64            # Large maximum window (aggressive)

# Detection examples
congestion timeout on               # Enable timeout-based congestion detection
congestion timeout off              # Disable timeout-based congestion detection
congestion dupack on                # Enable duplicate ACK-based congestion detection
congestion dupack off               # Disable duplicate ACK-based congestion detection
congestion threshold 2              # More sensitive duplicate ACK detection
congestion threshold 3              # Standard duplicate ACK threshold
congestion threshold 4              # Less sensitive duplicate ACK detection

# Combined options (can be specified on a single line)
congestion window 8 timeout on dupack on
congestion window 16 timeout off dupack on
congestion window 4 min-window 1 max-window 16
congestion min-window 2 max-window 32 threshold 3
congestion window 8 timeout on dupack off threshold 4
congestion window 12 min-window 3 max-window 48 timeout on dupack on threshold 3
```

## Command Combinations

### Network Conditions and Recommended Settings

#### For Stable, High-Bandwidth Networks

```bash
# Use Parallel mode with multiple threads
send myfile.txt 192.168.154.128 5000 -t 8

# Or use AIMD with aggressive settings
send myfile.txt 192.168.154.128 5000 -w 24 -min-w 6 -max-w 96
congestion window 24 min-window 6 max-window 96 timeout on dupack on
```

#### For Unstable or Congested Networks

```bash
# Use AIMD with conservative settings
send myfile.txt 192.168.154.128 5000 -w 4 -min-w 1 -max-w 16
congestion window 4 min-window 1 max-window 16 timeout on dupack on threshold 2

# Or use Token Bucket for controlled bandwidth
send myfile.txt 192.168.154.128 5000 -b 1024 -r 100
```

#### For Background Transfers

```bash
# Use QoS with low priority
send myfile.txt 192.168.154.128 5000 -p low

# Or use Token Bucket with very limited rate
send myfile.txt 192.168.154.128 5000 -b 512 -r 50
```

#### For Critical Transfers

```bash
# Use QoS with high priority
send myfile.txt 192.168.154.128 5000 -p high

# Or use simple Normal mode for reliability
send myfile.txt 192.168.154.128 5000
``` 