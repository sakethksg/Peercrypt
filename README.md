<div align="center">

# PeerCrypt 🔐

A decentralized file transfer application with strong encryption, advanced congestion control, and multiple transfer modes.

![PeerCrypt Logo](https://img.shields.io/badge/PeerCrypt-Secure%20File%20Transfer-blue?style=for-the-badge)

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
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
- [Usage](#-usage)
- [Configuration](#-configuration)
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
  </table>
</div>

## 🏗️ Architecture

PeerCrypt is built around a modular architecture with the following components:

```
src/
├── cli.py                    # Command-line interface
├── run_transfer_tests.py     # Test runner
├── test_transfer_modes.py    # Test suite
├── network/
│   └── peer_discovery.py     # Gossip-based peer discovery
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
<p>Basic file transfer with encryption for standard use cases.</p>
</details>

<details>
<summary><b>🪣 Token Bucket Mode</b></summary>
<p>Rate-limited transfers to ensure consistent bandwidth usage and prevent network flooding.</p>
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
</p>
</details>

<details>
<summary><b>🚦 QoS Mode</b></summary>
<p>Priority-based transfers with three levels: high, normal, and low.</p>
</details>

<details>
<summary><b>⚡ Parallel Mode</b></summary>
<p>Multi-threaded transfers to maximize throughput on high-bandwidth networks.</p>
</details>

<details>
<summary><b>📡 Multicast Mode</b></summary>
<p>Send files to multiple receivers simultaneously, perfect for distributing content to a group.</p>
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

You can customize environment variables in the docker-compose.yml file to change the default settings.

## 🖥️ Usage

### Running the Application

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/235224431-e8c8c12e-6826-47f1-89fb-2ddad83b3abf.gif" width="300">
</div>

Start the CLI interface:
```bash
python src/cli.py
```

Or with Docker:
```bash
docker run -it --network host peercrypt python src/cli.py
```

### Command-Line Arguments
```bash
python src/cli.py --host localhost --port 5000 --mode aimd --gossip-interval 5.0
```

<details>
<summary><b>Available Arguments</b></summary>
<ul>
  <li><code>--host</code>: Host address to bind to (default: localhost)</li>
  <li><code>--bootstrap-host</code>, <code>--bootstrap-port</code>: Connect to existing peer</li>
  <li><code>--mode</code>: Set initial transfer mode</li>
  <li><code>--gossip-interval</code>: Set peer discovery interval</li>
  <li><code>--no-gossip</code>: Disable gossip-based peer discovery</li>
</ul>
</details>

<details>
<summary><b>CLI Commands</b></summary>

#### Network Management
```
> join 192.168.1.100 5000         # Join network via bootstrap peer
> list-peers                       # List active peers
> gossip on                        # Enable gossip protocol
> gossip off                       # Disable gossip protocol
> gossip 10.0                      # Set gossip interval to 10 seconds
```

#### Transfer Mode Configuration
```
> set-mode normal                  # Set transfer mode to normal
> set-mode token-bucket            # Set rate-limited mode
> set-mode aimd                    # Set congestion control mode
> set-mode qos                     # Set quality of service mode
> set-mode parallel                # Set multi-threaded mode
> set-mode multicast               # Set multicast mode
```

#### File Transfers
```
> send file.txt 192.168.1.100 5000                     # Basic send
> send large-file.dat 192.168.1.100 5000 -w 16         # Send with 16KB window
> send video.mp4 192.168.1.100 5000 -p high            # Send with high priority
> send doc.pdf 192.168.1.100 5000 -t 4                 # Send with 4 threads
> send image.jpg 192.168.1.100 5000 -dual              # Send to two targets
> receive                                              # Receive a file
```
</details>

### Running Tests

Run all transfer tests:
```bash
python src/run_transfer_tests.py --mode all
```

<details>
<summary><b>Test Specific Modes</b></summary>
<p>
```bash
python src/run_transfer_tests.py --mode normal
python src/run_transfer_tests.py --mode aimd
python src/run_transfer_tests.py --mode aimd-congestion
python src/run_transfer_tests.py --mode multicast
```
</p>
</details>

## ⚙️ Configuration

### AIMD Mode Optimization

<div align="center">

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|------------------|
| Window Size | Initial congestion window | 1 KB | 1-64 KB |
| Min Window | Minimum window size | 1 KB | 1-4 KB |
| Max Window | Maximum window size | 64 KB | 16-128 KB |
| Timeout | Timeout-based detection | Enabled | Enabled for unreliable networks |
| DupACK | Triple duplicate ACK detection | Enabled | Enabled for high-bandwidth networks |
| Threshold | Duplicate ACK threshold | 3 | 2-5 |

</div>

## 💡 Recommendations

### Network-Specific Settings

<div align="center">

| Network Type | Recommended Mode | Window Size | Congestion Settings |
|--------------|------------------|-------------|---------------------|
| LAN (1 Gbps) | Parallel | 64 KB | DupACK only, 4 threads |
| WiFi (stable) | AIMD | 16-32 KB | Both detection mechanisms |
| WiFi (unstable) | AIMD | 4-8 KB | Both, smaller timeout |
| Mobile network | Token Bucket | 8 KB | 512 KB/s rate limit |
| Low bandwidth | Normal | 1-2 KB | Default |

</div>

## 🛠️ Development

- Written in Python 3.7+
- Uses PyCryptodome for AES-256 encryption
- Implements RFC 6298 for RTO calculation
- Modular architecture for easy extension

<p align="center">
  <img src="https://user-images.githubusercontent.com/74038190/213910845-af37a709-8995-40d6-be59-724526e3c3d7.gif" width="300">
</p>

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/216644497-1951db19-8f3d-4e44-ac08-8e9d7e0d94a7.gif" alt="Thanks" width="400">
  
  **Made with ❤️ by [Your Name]**
</div> 