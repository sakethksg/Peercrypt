<div align="center">

# PeerCrypt 🔐

A decentralized file transfer application with strong encryption, advanced congestion control, multiple transfer modes, and robust peer connections.

![PeerCrypt Logo](https://img.shields.io/badge/PeerCrypt-Secure%20File%20Transfer-blue?style=for-the-badge)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)

</div>


## 📋 Table of Contents
- [Features](#-features)
- [Architecture](#-architecture)
- [Transfer Modes](#-transfer-modes)
- [Installation](#-installation)
  - [Standard Installation](#standard-installation)
  - [Docker Installation](#docker-installation)
  - [Docker Compose Installation](#docker-compose)
- [Testing](#-testing)
  - [Running Tests](#running-tests)
  - [Test Output Files](#test-output-files)
- [Usage](#-usage)
  - [Command-Line Options](#command-line-options)
  - [Interactive Commands](#interactive-commands)
  - [Commands Reference](#commands-reference)
- [Configuration](#-configuration)
  - [Environment Variables](#environment-variables)
  - [Gossip Network Configuration](#gossip-network-configuration)
  - [AIMD Congestion Control](#aimd-congestion-control-configuration)
  - [Peer Connection Management](#peer-connection-management)
- [Recommendations](#-recommendations)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

<div align="center">
  <table>
    <tr>
      <td align="center">🔒</td>
      <td><b>End-to-End Encryption</b>: All file transfers secured using AES-256 in CBC mode</td>
    </tr>
    <tr>
      <td align="center">🔄</td>
      <td><b>Multiple Transfer Modes</b>: Choose the optimal mode for your network conditions</td>
    </tr>
    <tr>
      <td align="center">📊</td>
      <td><b>Adaptive Congestion Control</b>: AIMD algorithm dynamically adjusts to network conditions</td>
    </tr>
    <tr>
      <td align="center">🌐</td>
      <td><b>Decentralized Network</b>: Gossip-based peer discovery for resilient operation</td>
    </tr>
    <tr>
      <td align="center">🔍</td>
      <td><b>Comprehensive Statistics</b>: Detailed metrics for all file transfers</td>
    </tr>
    <tr>
      <td align="center">🚦</td>
      <td><b>Quality of Service</b>: Priority-based transfers for important files</td>
    </tr>
    <tr>
      <td align="center">⚡</td>
      <td><b>High Performance</b>: Parallel transfers for maximizing throughput</td>
    </tr>
    <tr>
      <td align="center">📡</td>
      <td><b>Multicast Support</b>: Send to multiple receivers simultaneously</td>
    </tr>
    <tr>
      <td align="center">🔌</td>
      <td><b>Robust Peer Connections</b>: Automatic health checks and connection recovery</td>
    </tr>
    <tr>
      <td align="center">⭐</td>
      <td><b>Reliability Scoring</b>: Dynamic peer reliability assessment for smart routing</td>
    </tr>
  </table>
</div>

## 🏗️ Architecture

PeerCrypt is built around a modular architecture with the following components:

```
src/
├── cli.py                    # Command-line interface
├── network/
│   └── peer_discovery.py     # Gossip-based peer discovery with robust connection handling
├── transfer_modes/
│   ├── normal_mode.py        # Basic transfer
│   ├── token_bucket_mode.py  # Rate-limited transfer
│   ├── aimd_mode.py          # Congestion-controlled transfer
│   ├── qos_mode.py           # Priority-based transfer
│   ├── parallel_mode.py      # Multi-threaded transfer
│   └── multicast_mode.py     # One-to-many transfer
└── utils/
    └── encryption.py         # AES-256 encryption
```

## 🚀 Transfer Modes

<details>
<summary><b>🔄 Normal Mode</b></summary>
<p>Basic file transfer with encryption for standard use cases. This is the simplest and most reliable mode, suitable for most everyday transfers in stable network conditions.</p>
</details>

<details>
<summary><b>🪣 Token Bucket Mode</b></summary>
<p>Rate-limited transfers to ensure consistent bandwidth usage and prevent network flooding. The token bucket algorithm allows for controlled bursts while maintaining an average rate limit, making it ideal for background transfers that shouldn't interfere with other network traffic.</p>
</details>

<details>
<summary><b>📈 AIMD Mode</b></summary>
<p>
The AIMD mode implements two standard congestion detection mechanisms:

<ul>
  <li><b>Timeout-Based Detection</b>: Detects packet loss when ACKs aren't received within the calculated timeout</li>
  <li><b>Triple Duplicate ACK Detection</b>: Detects packet loss when receiving the same ACK multiple times</li>
</ul>

Congestion Window Management:
<ul>
  <li><b>Additive Increase</b>: Window grows by 1KB for each successful transmission</li>
  <li><b>Multiplicative Decrease</b>: Window halves when congestion is detected</li>
</ul>

This mode is ideal for transfers over unstable or congested networks, as it dynamically adjusts to available bandwidth.
</p>
</details>

<details>
<summary><b>🚦 QoS Mode</b></summary>
<p>Priority-based transfers with three levels: normal (1), high (2), and highest (3). This mode ensures that important files get transferred with higher priority when multiple transfers are occurring simultaneously. The QoS manager allocates bandwidth proportionally based on priority levels.</p>
</details>

<details>
<summary><b>⚡ Parallel Mode</b></summary>
<p>Multi-threaded transfers to maximize throughput on high-bandwidth networks. This mode splits files into chunks and transfers them concurrently, which can significantly increase performance especially on high-latency connections. The number of threads is configurable (default: 4).</p>
</details>

<details>
<summary><b>📡 Multicast Mode</b></summary>
<p>Send files to multiple receivers simultaneously, perfect for distributing content to a group. This mode efficiently handles one-to-many transfers by establishing individual connections to each target while managing them collectively.</p>
</details>

## 🔌 Robust Peer Connections

<details>
<summary><b>🔄 Reliability Scoring</b></summary>
<p>Each peer in the network is assigned a reliability score (0.0-1.0) that dynamically adjusts based on connection quality. Successful interactions increase reliability, while failures decrease it. This score is used to prioritize connections to the most stable peers.</p>
</details>

<details>
<summary><b>🔍 Health Check System</b></summary>
<p>PeerCrypt implements an automatic health check system that periodically verifies connectivity with peers. When inactive peers are detected, the system attempts to re-establish connections without manual intervention. Before file transfers, destination peers are checked to ensure they're reachable.</p>
</details>

<details>
<summary><b>🔁 Retry Mechanism</b></summary>
<p>All network operations include configurable retry logic with exponential backoff. When a connection fails, the system automatically attempts to reconnect multiple times with increasing timeouts to handle temporary network disruptions gracefully.</p>
</details>

<details>
<summary><b>📊 Connection Quality Metrics</b></summary>
<p>The system tracks round-trip time (RTT) and failure counts for each peer. These metrics help identify network problems and allow the system to adapt to changing network conditions. The CLI provides detailed visibility into connection quality.</p>
</details>

## 📥 Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/username/peercrypt.git
cd peercrypt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The project requires Python 3.9+ and the following dependencies:
- cryptography >= 41.0.0
- matplotlib >= 3.7.0
- numpy >= 1.24.0
- pandas >= 2.0.0
- pycryptodome >= 3.19.0
- colorama >= 0.4.6
- pyreadline3 >= 3.4.1
- tqdm >= 4.45.0

### Docker Installation

1. Build the Docker image:
```bash
docker build -t peercrypt .
```

2. Run the container:
```bash
docker run -it --network host peercrypt
```

For persistent storage:
```bash
docker run -it -v $(pwd)/data:/app/data --network host peercrypt
```

### Docker Compose

For easier deployment, you can use Docker Compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

You can customize environment variables in the docker-compose.yml file to change the default settings:

```yaml
environment:
  # Transfer mode configuration
  - DEFAULT_MODE=aimd  # Options: normal, token-bucket, aimd, qos, parallel, multicast
  
  # Network discovery configuration
  - GOSSIP_INTERVAL=5.0  # Interval in seconds for peer discovery
  
  # Uncomment to disable gossip-based peer discovery on startup
  # - DISABLE_GOSSIP=true
  
  # Advanced AIMD congestion control (for aimd mode)
  # - AIMD_WINDOW=32  # Initial window size in KB
  # - AIMD_MIN_WINDOW=8  # Minimum window size in KB
  # - AIMD_MAX_WINDOW=128  # Maximum window size in KB
  
  # Parallel mode configuration
  # - PARALLEL_THREADS=4  # Number of threads for parallel transfers
```

For easier configuration, you can use the provided script to generate a `.env` file:

```bash
# Run the interactive setup script
./create_env.sh

# Or create/edit .env manually with these settings:
cat > .env << EOF
# PeerCrypt Environment Variables

# Transfer mode configuration
DEFAULT_MODE=aimd

# Network discovery configuration
GOSSIP_INTERVAL=5.0

# Uncomment to disable gossip-based peer discovery
# DISABLE_GOSSIP=true

# AIMD congestion control settings
AIMD_WINDOW=32
AIMD_MIN_WINDOW=8
AIMD_MAX_WINDOW=128

# Parallel mode settings
PARALLEL_THREADS=4
EOF
```

## 🧪 Testing

PeerCrypt includes comprehensive testing for all transfer modes to ensure reliability and performance.

### Running Tests

Run all transfer mode tests:
```bash
python test_all_modes.py
```

Test a specific transfer mode:
```bash
python run_mode_test.py <mode>
```

Available modes: `normal`, `token-bucket`, `aimd`, `qos`, `parallel`, `multicast`, `all`

Example to test just the AIMD mode:
```bash
python run_mode_test.py aimd
```

These tests verify every transfer mode with various file sizes and configurations to ensure correct operation.

### Test Output Files

Tests generate temporary files and statistics that are excluded from version control:

- `*_test.txt`: Test input/output files for verification
- `received_test.txt`: Files received during testing
- `test.txt`: Generic test file
- `myfile.txt`: Another test file
- `*_stats.json`, `*_stats.csv`: Performance statistics from tests
- `aimd_congestion_stats.json`: AIMD congestion control statistics

These files are automatically added to `.gitignore` to avoid cluttering the repository with test artifacts.

<details>
<summary><b>Test Details</b></summary>
<p>
The test suite performs the following for each mode:

- Tests with multiple file sizes (1KB, 10KB, and 100KB)
- Verifies successful transfers through file integrity checks
- Tests special features of each mode:
  - Token Bucket: Tests rate limiting with different bucket sizes
  - AIMD: Tests adaptive window sizing and congestion response
  - QoS: Tests different priority levels
  - Parallel: Tests different thread counts (2 and 4)
  - Multicast: Tests sending to multiple targets

Tests are designed to use dynamic port allocation to avoid conflicts and include proper cleanup between tests.
</p>
</details>

## 🖥️ Usage

### Command-Line Options

Start the CLI interface with various configuration options:

```bash
python src/cli.py [OPTIONS]
```

Available options:
```
--host HOST                     Host to bind to (default: localhost)
--bootstrap-host HOST           Bootstrap peer host
--bootstrap-port PORT           Bootstrap peer port
--mode MODE                     Initial transfer mode (choices: normal, token-bucket, aimd, qos, parallel, multicast)
--gossip-interval INTERVAL      Interval in seconds for gossip-based peer discovery (default: 5.0)
--no-gossip                     Disable gossip-based peer discovery on startup
--max-retries N                 Set maximum connection retry attempts (default: 3)
--timeout SEC                   Set initial connection timeout in seconds (default: 3.0)
--health-check-interval N       Set interval between health checks in seconds (default: 10.0)
```

Using Docker:
```bash
docker run -it --network host peercrypt python src/cli.py --host 0.0.0.0 --mode aimd --max-retries 4 --timeout 5.0
```

### Interactive Commands

PeerCrypt provides a rich set of interactive commands to control file transfers and network behavior:

#### Basic Commands
```
help                            Show available commands and current status
status                          Show current mode and configuration
quit or exit                    Exit the application
```

#### Network and Peer Management
```
list-peers                      Show discovered peers and reliability scores
join <host> <port>              Join an existing network through a peer
health-check <host> <port>      Check if a peer is reachable
reconnect <host> <port>         Attempt to reconnect to a problematic peer
gossip on|off|<interval>        Configure peer discovery (on/off/interval in seconds)
```

#### Transfer Mode Control
```
set-mode <mode>                 Change the current transfer mode (normal|token-bucket|aimd|qos|parallel|multicast)
congestion <options>            Configure AIMD congestion control parameters
```

#### File Transfer
```
send <file> <host> <port>       Send a file to a specific host
receive                         Start receiving a file
multicast-receive [port-range]  Start multicast receiver (also shortened as "mreceive")
```

#### Send File Options

When sending files, you can specify mode-specific options:

For Parallel Mode:
```
send file.txt host port -t 4  # Use 4 threads
```

For Token Bucket Mode:
```
send file.txt host port -b 1024 -r 512  # Bucket size 1024, rate 512 bytes/sec
```

For QoS Mode:
```
send file.txt host port -p high  # Priority: normal, high, highest
```

For AIMD Mode:
```
send file.txt host port -w 32 -min-w 8 -max-w 128  # Window sizes in KB
send file.txt host port -no-timeout  # Disable timeout detection
send file.txt host port -no-dupack  # Disable duplicate ACK detection
```

For Multicast Mode:
```
send file.txt host port -m              # Will prompt for additional targets
send file.txt host port -dual           # Send to exactly two targets
```

#### Connection Verification

Before sending files, PeerCrypt automatically performs a health check on target peers:
- Displays warning if peers are unreachable
- Offers option to proceed or abort transfer
- For multicast, shows which targets are unreachable
- Updates reliability scores based on successful or failed transfers

### Commands Reference

For a comprehensive reference of all PeerCrypt commands and their options, see the [commands.md](commands.md) file, which includes:

- Basic commands for general CLI interaction
- Network and peer management commands
- File transfer commands with all available options
- Detailed options for each transfer mode
- Advanced congestion control configuration
- Recommended command combinations for different network conditions

This document provides examples and explanations for all commands and serves as the definitive reference for using PeerCrypt effectively.

## 🛠️ Configuration

### Environment Variables

When using Docker or Docker Compose, you can configure PeerCrypt using environment variables:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| DEFAULT_MODE | Initial transfer mode | normal | aimd |
| GOSSIP_INTERVAL | Interval for peer discovery in seconds | 5.0 | 10.0 |
| DISABLE_GOSSIP | Disable peer discovery on startup | false | true |
| AIMD_WINDOW | Initial congestion window size in KB | 16 | 32 |
| AIMD_MIN_WINDOW | Minimum congestion window size in KB | 4 | 8 |
| AIMD_MAX_WINDOW | Maximum congestion window size in KB | 64 | 128 |
| PARALLEL_THREADS | Default threads for parallel mode | 4 | 8 |
| MAX_RETRIES | Maximum connection retry attempts | 3 | 5 |
| CONNECTION_TIMEOUT | Initial connection timeout in seconds | 3.0 | 5.0 |
| HEALTH_CHECK_INTERVAL | Interval between health checks in seconds | 10.0 | 20.0 |

### Gossip Network Configuration

Configure the peer discovery mechanism:

```
gossip on                   # Enable gossip-based peer discovery
gossip off                  # Disable gossip-based peer discovery
gossip interval 10          # Set the gossip interval to 10 seconds
```

### AIMD Congestion Control Configuration

Configure congestion control parameters for AIMD mode:

```
congestion window 32        # Set initial window size to 32 KB
congestion min-window 8     # Set minimum window size to 8 KB
congestion max-window 128   # Set maximum window size to 128 KB
congestion timeout on/off   # Enable/disable timeout-based detection
congestion dupack on/off    # Enable/disable duplicate ACK detection
```

### Peer Connection Management

The robust peer connection system can be configured through both command-line arguments and runtime commands:

#### Command-line Arguments:

```bash
--max-retries N            Set maximum connection retry attempts (default: 3)
--timeout SEC              Set initial connection timeout in seconds (default: 3.0)
--health-check-interval N  Set interval between health checks in seconds (default: 10.0)
```

#### Runtime Commands:

```
health-check <host> <port>  Manually check if a peer is reachable
reconnect <host> <port>     Attempt to reconnect to a problematic peer
list-peers                  Show all peers with reliability scores
```

#### Configuration Best Practices:

1. For **stable networks**, you can reduce overhead:
   ```bash
   --max-retries 2 --timeout 2.0 --health-check-interval 30.0
   ```

2. For **unstable or high-latency networks**, increase resilience:
   ```bash
   --max-retries 5 --timeout 5.0 --health-check-interval 15.0
   ```

3. For **mobile or frequently changing networks**, optimize for discovery:
   ```bash
   --max-retries 3 --timeout 4.0 --health-check-interval 8.0
   ```

The peer connection system will automatically adapt to network conditions, but these settings provide a starting point for optimization.

## 🚨 Recommendations

For optimal performance in different network conditions:

- **Stable, high-bandwidth networks**: Use Parallel mode with 4-8 threads
- **Unstable or congested networks**: Use AIMD mode
- **Background transfers**: Use Token Bucket mode with appropriate rate limits
- **Multiple priority transfers**: Use QoS mode
- **Distribution to multiple receivers**: Use Multicast mode

## 🔧 Development

### Adding a New Transfer Mode

1. Create a new file in `src/transfer_modes/` following the existing structure
2. Implement the required methods
3. Register the mode in `cli.py`

### Debugging

Enable verbose logging for debugging:

```bash
python src/cli.py --debug
```

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/216644497-1951db19-8f3d-4e44-ac08-8e9d7e0d94a7.gif" alt="Thanks" width="400">
  
  **Made with ❤️ by Kollipara Sai Govinda Saketh and Team**
</div> 