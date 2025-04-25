<div align="center">

# PeerCrypt 🔐

A **Computer Networks project** implementing a decentralized file transfer application with strong encryption, advanced congestion control, multiple transfer modes, and robust peer connections.



[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg?style=flat-square)](https://github.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)](https://www.docker.com/)

</div>

<div align="center">
  <h3>Secure, Fast, and Reliable P2P File Transfers</h3>
</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Transfer Modes](#-transfer-modes)
- [Computer Networks Concepts](#-computer-networks-concepts)
- [Protocol Specifications](#-protocol-specifications)
- [Mathematical Analysis](#-mathematical-analysis)
- [Research Background](#-research-background)
- [Related Work Comparison](#-related-work-comparison)
- [Installation](#-installation)
- [Testing](#-testing)
- [Usage Guide](#-usage-guide)
- [Configuration](#-configuration)
- [Experiment Results and Analysis](#-experiment-results-and-analysis)
- [Future Work](#-future-work)
- [Recommendations](#-recommendations)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [📖 Commands Reference](commands.md)

---

## 🔍 Overview

PeerCrypt is an advanced Computer Networks project that implements a sophisticated file transfer solution leveraging multiple networking paradigms and protocols. It serves as a comprehensive demonstration of networking concepts including:

- **Transport Layer Implementation**: Custom application-level protocols built on TCP
- **Congestion Control Algorithms**: Implementation of AIMD and other flow control mechanisms
- **Peer-to-Peer Architecture**: Decentralized network topology with direct peer connections
- **Network Reliability**: Techniques for ensuring data delivery across unreliable networks
- **Performance Optimization**: Methods to maximize throughput under various network conditions

This project applies theoretical networking concepts to practical challenges in distributed file transfer, making it an ideal educational tool for understanding Computer Networks principles in action.

---

## ✨ Features

<div align="center">
  <table>
    <tr>
      <td align="center" width="80"><h3>🔒</h3></td>
      <td><b>End-to-End Encryption</b><br><small>All file transfers secured using AES-256 in CBC mode with HMAC authentication</small></td>
    </tr>
    <tr>
      <td align="center"><h3>🔄</h3></td>
      <td><b>Multiple Transfer Modes</b><br><small>Choose the optimal mode for your network conditions</small></td>
    </tr>
    <tr>
      <td align="center"><h3>📊</h3></td>
      <td><b>Adaptive Congestion Control</b><br><small>AIMD algorithm dynamically adjusts to network conditions</small></td>
    </tr>
    <tr>
      <td align="center"><h3>🌐</h3></td>
      <td><b>Decentralized Network</b><br><small>Gossip-based peer discovery for resilient operation</small></td>
    </tr>
    <tr>
      <td align="center"><h3>🔍</h3></td>
      <td><b>Comprehensive Statistics</b><br><small>Detailed metrics for all file transfers</small></td>
    </tr>
    <tr>
      <td align="center"><h3>🚦</h3></td>
      <td><b>Quality of Service</b><br><small>Priority-based transfers for important files</small></td>
    </tr>
    <tr>
      <td align="center"><h3>⚡</h3></td>
      <td><b>High Performance</b><br><small>Parallel transfers for maximizing throughput</small></td>
    </tr>
    <tr>
      <td align="center"><h3>📡</h3></td>
      <td><b>Multicast Support</b><br><small>Send to multiple receivers simultaneously</small></td>
    </tr>
    <tr>
      <td align="center"><h3>🔌</h3></td>
      <td><b>Robust Peer Connections</b><br><small>Automatic health checks and connection recovery</small></td>
    </tr>
    <tr>
      <td align="center"><h3>⭐</h3></td>
      <td><b>Reliability Scoring</b><br><small>Dynamic peer reliability assessment for smart routing</small></td>
    </tr>
  </table>
</div>

---

## 💻 Technology Stack

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyCryptodome-AES_256-orange.svg?style=for-the-badge&logo=lock" alt="PyCryptodome">
  <img src="https://img.shields.io/badge/Matplotlib-Visualization-blue.svg?style=for-the-badge&logo=chart-pie" alt="Matplotlib">
  <img src="https://img.shields.io/badge/Socket-TCP-success.svg?style=for-the-badge" alt="TCP">
  <img src="https://img.shields.io/badge/Threading-Parallel-purple.svg?style=for-the-badge" alt="Parallel">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg?style=for-the-badge&logo=docker" alt="Docker">
</div>

<div class="tech-container" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">

<div class="tech-section" style="border-radius: 10px; padding: 15px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">Core Technologies</h3>
  <ul>
    <li><strong>Python 3.9+</strong>: Primary implementation language</li>
    <li><strong>Cryptography</strong>: AES-256 encryption using PyCryptodome</li>
    <li><strong>Socket Programming</strong>: Custom TCP-based protocol for peer-to-peer communication</li>
    <li><strong>Multithreading</strong>: Parallel processing for concurrent transfers</li>
  </ul>
</div>

<div class="tech-section" style="border-radius: 10px; padding: 15px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">Python Libraries</h3>
  <ul>
    <li><strong>PyCryptodome</strong>: Advanced cryptographic library for encryption</li>
    <li><strong>Matplotlib</strong>: Data visualization for performance metrics</li>
    <li><strong>Colorama</strong>: Terminal colorization for the CLI</li>
    <li><strong>pyreadline3</strong>: Enhanced CLI input handling</li>
    <li><strong>tqdm</strong>: Progress bars for file transfers</li>
  </ul>
</div>

<div class="tech-section" style="border-radius: 10px; padding: 15px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">Library Versions</h3>
  <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
    <div>
      <code style="background-color: #1a1e24; padding: 5px; border-radius: 3px; font-size: 0.9em; color: #e6edf3;">cryptography >= 41.0.0</code>
    </div>
    <div>
      <code style="background-color: #1a1e24; padding: 5px; border-radius: 3px; font-size: 0.9em; color: #e6edf3;">matplotlib >= 3.7.0</code>
    </div>
    <div>
      <code style="background-color: #1a1e24; padding: 5px; border-radius: 3px; font-size: 0.9em; color: #e6edf3;">pycryptodome >= 3.19.0</code>
    </div>
    <div>
      <code style="background-color: #1a1e24; padding: 5px; border-radius: 3px; font-size: 0.9em; color: #e6edf3;">colorama >= 0.4.6</code>
    </div>
    <div>
      <code style="background-color: #1a1e24; padding: 5px; border-radius: 3px; font-size: 0.9em; color: #e6edf3;">pyreadline3 >= 3.4.1</code>
    </div>
    <div>
      <code style="background-color: #1a1e24; padding: 5px; border-radius: 3px; font-size: 0.9em; color: #e6edf3;">tqdm >= 4.45.0</code>
    </div>
  </div>
</div>

<div class="tech-section" style="border-radius: 10px; padding: 15px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">Security Features</h3>
  <ul>
    <li><strong>AES-256-CBC</strong>: For file encryption with 256-bit keys</li>
    <li><strong>HMAC-SHA256</strong>: For message authentication</li>
    <li><strong>PBKDF2</strong>: For key derivation with 100,000 iterations</li>
    <li><strong>Secure Random</strong>: Cryptographically secure random number generation</li>
  </ul>
</div>

<div class="tech-section" style="border-radius: 10px; padding: 15px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">Network Protocols</h3>
  <ul>
    <li><strong>Gossip Protocol</strong>: For decentralized peer discovery</li>
    <li><strong>TCP</strong>: Reliable transport layer protocol</li>
    <li><strong>Custom Application Protocol</strong>: For file transfer metadata</li>
  </ul>
</div>

<div class="tech-section" style="border-radius: 10px; padding: 15px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">Performance Optimization</h3>
  <ul>
    <li><strong>AIMD Algorithm</strong>: Additive Increase Multiplicative Decrease for congestion control</li>
    <li><strong>Token Bucket Algorithm</strong>: For rate-limited transfers</li>
    <li><strong>Parallel Chunking</strong>: For high-throughput transfers</li>
    <li><strong>Connection Pooling</strong>: For efficient peer connections</li>
  </ul>
</div>

</div>

---

## 🏗️ Architecture

PeerCrypt demonstrates a layered network architecture following the principles of the OSI and TCP/IP models, with implementation focuses at the Application, Transport, and Network layers.

### Network Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│                                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐     │
│  │  Normal │   │  Token  │   │  AIMD   │   │   QoS   │     │
│  │  Mode   │   │ Bucket  │   │  Mode   │   │  Mode   │     │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘     │
│                                                             │
│  ┌─────────┐   ┌─────────┐      ┌───────────────────┐      │
│  │ Parallel│   │Multicast│      │  Encryption Layer │      │
│  │  Mode   │   │  Mode   │      │  (AES-256-CBC)    │      │
│  └─────────┘   └─────────┘      └───────────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                      Transport Layer                         │
│                                                             │
│  ┌─────────────────┐   ┌──────────────────────────────┐    │
│  │  Socket API     │   │      Flow Control            │    │
│  │  (TCP-based)    │   │  (Window & Rate Limiting)    │    │
│  └─────────────────┘   └──────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                       Network Layer                          │
│                                                             │
│  ┌─────────────────┐   ┌──────────────────────────────┐    │
│  │ Gossip Protocol │   │         NAT Traversal        │    │
│  │ (Peer Discovery)│   │       (IP Connectivity)      │    │
│  └─────────────────┘   └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

PeerCrypt is built around a modular architecture with clear separation of concerns:

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

---

## 🚀 Transfer Modes

PeerCrypt offers specialized transfer modes optimized for different network scenarios:

<div class="mode-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">

<div class="mode-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">🔄 Normal Mode</h3>
  <p>Basic file transfer with encryption for standard use cases. Most reliable for stable networks.</p>
  <p><strong>Best for:</strong> Everyday transfers in stable network conditions</p>
</div>

<div class="mode-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">🪣 Token Bucket Mode</h3>
  <p>Rate-limited transfers to ensure consistent bandwidth usage and prevent network flooding.</p>
  <p><strong>Best for:</strong> Background transfers that shouldn't interfere with other traffic</p>
</div>

<div class="mode-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">📈 AIMD Mode</h3>
  <p>Implements TCP-like congestion control with Additive Increase Multiplicative Decrease.</p>
  <p><strong>Best for:</strong> Transfers over unstable or congested networks</p>
</div>

<div class="mode-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">🚦 QoS Mode</h3>
  <p>Priority-based transfers with three levels: normal, high, and highest.</p>
  <p><strong>Best for:</strong> Managing multiple transfers with different importance levels</p>
</div>

<div class="mode-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">⚡ Parallel Mode</h3>
  <p>Multi-threaded transfers to maximize throughput on high-bandwidth networks.</p>
  <p><strong>Best for:</strong> High-speed transfers on reliable networks</p>
</div>

<div class="mode-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h3 style="color: #58a6ff;">📡 Multicast Mode</h3>
  <p>Send files to multiple receivers simultaneously.</p>
  <p><strong>Best for:</strong> Distribution to multiple targets efficiently</p>
</div>

</div>

### Detailed Mode Descriptions

#### 🔄 Normal Mode
Basic file transfer with encryption for standard use cases. This is the simplest and most reliable mode, suitable for most everyday transfers in stable network conditions.

#### 🪣 Token Bucket Mode
Rate-limited transfers to ensure consistent bandwidth usage and prevent network flooding. The token bucket algorithm allows for controlled bursts while maintaining an average rate limit, making it ideal for background transfers that shouldn't interfere with other network traffic.

#### 📈 AIMD Mode
The AIMD mode implements two standard congestion detection mechanisms:
- **Timeout-Based Detection**: Detects packet loss when ACKs aren't received within the calculated timeout
- **Triple Duplicate ACK Detection**: Detects packet loss when receiving the same ACK multiple times

Congestion Window Management:
- **Additive Increase**: Window grows by 1KB for each successful transmission
- **Multiplicative Decrease**: Window halves when congestion is detected

This mode is ideal for transfers over unstable or congested networks, as it dynamically adjusts to available bandwidth.

#### 🚦 QoS Mode
Priority-based transfers with three levels: normal (1), high (2), and highest (3). This mode ensures that important files get transferred with higher priority when multiple transfers are occurring simultaneously. The QoS manager allocates bandwidth proportionally based on priority levels.

#### ⚡ Parallel Mode
Multi-threaded transfers to maximize throughput on high-bandwidth networks. This mode splits files into chunks and transfers them concurrently, which can significantly increase performance especially on high-latency connections. The number of threads is configurable (default: 4).

#### 📡 Multicast Mode
Send files to multiple receivers simultaneously, perfect for distributing content to a group. This mode efficiently handles one-to-many transfers by establishing individual connections to each target while managing them collectively.

---

## 🔌 Robust Peer Connections

PeerCrypt implements sophisticated mechanisms to maintain reliable peer connections:

<div class="grid-container" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
  <div class="grid-item" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h3 style="color: #58a6ff;">🔄 Reliability Scoring</h3>
    <p>Each peer is assigned a dynamic reliability score (0.0-1.0) based on connection quality, used to prioritize stable peers.</p>
  </div>
  <div class="grid-item" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h3 style="color: #58a6ff;">🔍 Health Check System</h3>
    <p>Automatic verification of peer connectivity with re-establishment of connections to inactive peers.</p>
  </div>
  <div class="grid-item" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h3 style="color: #58a6ff;">🔁 Retry Mechanism</h3>
    <p>Configurable retry logic with exponential backoff for graceful handling of temporary network disruptions.</p>
  </div>
  <div class="grid-item" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h3 style="color: #58a6ff;">📊 Connection Quality Metrics</h3>
    <p>Tracking of RTT and failure counts for network problem identification and adaptation.</p>
  </div>
</div>

---

## 🌐 Computer Networks Concepts

PeerCrypt implements several advanced computer networking concepts that align with standard Computer Networks curricula:

### TCP Protocol and Socket Programming

- **Socket API**: Creates TCP connections between peers, handling network addressing and connection establishment
- **Three-Way Handshake**: Leverages TCP's connection establishment process for reliable peer connections
- **Connection-Oriented Communication**: Ensures data reliability and ordered delivery
- **TCP Flow Control**: Implements application-layer flow control for fine-grained transfer management

**Academic Reference**: The implementation follows principles described in Kurose and Ross's "Computer Networking: A Top-Down Approach" (Chapter 3: Transport Layer).

### Congestion Control Mechanisms

- **AIMD Algorithm**: Similar to TCP's congestion avoidance with:
  - **Slow Start**: Beginning with a small window that grows exponentially
  - **Congestion Avoidance**: Linear growth after threshold
  - **Fast Recovery**: Quickly recovering from minor packet loss
- **Congestion Window**: Dynamic sizing based on network conditions
- **Timeout Detection**: RTT-based timeout calculation using Jacobson's algorithm
- **Triple Duplicate ACK Detection**: Fast retransmission when receiving three duplicate ACKs

**Academic Reference**: Implementation based on Van Jacobson's "Congestion Avoidance and Control" paper and RFC 5681.

### Network Layer Concepts

- **IP Addressing**: Support for both IPv4 and IPv6
- **Subnetting**: Works across different subnets with proper routing
- **NAT Traversal**: Techniques for peers behind NAT

**Academic Reference**: Follows concepts from Peterson and Davie's "Computer Networks: A Systems Approach" (Chapter 4: The Network Layer).

### Peer Discovery and Overlay Networks

- **Gossip Protocol**: Epidemic-style peer information dissemination
- **Overlay Network**: Logical network layered on physical infrastructure
- **Health Monitoring**: Active and passive monitoring of peer availability
- **Topology Management**: Dynamic adjustment of peer connections

**Academic Reference**: Based on principles described in "Gossip-based Peer Sampling" by Jelasity et al.

### Quality of Service

- **Traffic Prioritization**: Priority queues for different traffic classes
- **Resource Allocation**: Dynamic bandwidth allocation based on priority
- **Differentiated Services**: Treatment according to assigned priority

### Rate Control Algorithms

- **Token Bucket Algorithm**: Controlled bursts while maintaining average rate limits
  - **Bucket Size**: Controls maximum burst size
  - **Token Rate**: Controls sustained throughput

### Additional Network Concepts

- **Multi-Path and Parallel Transfers**: Multiple connections for higher throughput
- **Network Reliability Engineering**: Fault detection and circuit breaker patterns
- **End-to-End Encryption**: Secure transport with minimal intermediary requirements
- **Application-Layer Multicast**: Efficient one-to-many delivery

---

## 📝 Protocol Specifications

PeerCrypt implements several custom network protocols for different aspects of the system. These protocols are formally documented below:

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">1. File Transfer Protocol (FTP)</h4>
  
  <p>PeerCrypt implements a custom application-layer File Transfer Protocol optimized for secure peer-to-peer communication. This protocol is specifically designed to address the security and reliability challenges in decentralized networks.</p>
  
  <h5 style="color: #58a6ff; margin-top: 15px;">1.1 Packet Format</h5>
  
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |    Version    |     Type      |           Sequence #          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                          Timestamp                            |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |      Data Length (bytes)      |           Checksum            |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                         Flags (16 bits)                       |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                                                               |
  |                       Authentication Token                    |
  |                            (64 bits)                          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                                                               |
  |                            Payload                            |
  |                                                               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  </pre>
  
  <h5 style="color: #58a6ff; margin-top: 15px;">1.2 Field Descriptions</h5>
  
  <ul>
    <li><strong>Version</strong> (8 bits): Protocol version identifier
      <ul>
        <li>0x01: Current implementation version</li>
        <li>Allows for future protocol evolution while maintaining backward compatibility</li>
      </ul>
    </li>
    <li><strong>Type</strong> (8 bits): Packet type identifier
      <ul>
        <li>0x01: DATA - File data packet</li>
        <li>0x02: ACK - Acknowledgment for received packet</li>
        <li>0x03: INIT - Transfer initialization with metadata</li>
        <li>0x04: FIN - Transfer completion notification</li>
        <li>0x05: RST - Connection reset</li>
        <li>0x06: METADATA - File metadata packet</li>
        <li>0x07: ERROR - Error notification</li>
        <li>0x08: PAUSE - Flow control signal</li>
        <li>0x09: RESUME - Flow control signal</li>
      </ul>
    </li>
    <li><strong>Sequence #</strong> (16 bits): Packet sequence number
      <ul>
        <li>Wraps around to 0 after reaching 65,535</li>
        <li>Used for in-order delivery and duplicate detection</li>
      </ul>
    </li>
    <li><strong>Timestamp</strong> (32 bits): Unix timestamp in milliseconds
      <ul>
        <li>Used for RTT calculation and congestion control</li>
        <li>Enables timeout-based retransmission decisions</li>
      </ul>
    </li>
    <li><strong>Data Length</strong> (16 bits): Length of payload in bytes
      <ul>
        <li>Maximum value: 65,535 bytes</li>
        <li>Typical Maximum Transmission Unit (MTU): 1,400 bytes to avoid IP fragmentation</li>
      </ul>
    </li>
    <li><strong>Checksum</strong> (16 bits): CRC-16 of the header and payload
      <ul>
        <li>Polynomial: 0x8005 (CRC-16-IBM)</li>
        <li>Initial value: 0xFFFF</li>
        <li>Used for error detection at the packet level</li>
      </ul>
    </li>
    <li><strong>Flags</strong> (16 bits): Bitfield for packet properties
      <ul>
        <li>0x0001: Encrypted - Payload is encrypted</li>
        <li>0x0002: Fragmented - Packet is part of fragmented data</li>
        <li>0x0004: Last Fragment - Last packet in fragmented sequence</li>
        <li>0x0008: High Priority - Higher QoS priority</li>
        <li>0x0010: Requires ACK - Explicit acknowledgment required</li>
        <li>0x0020: Compressed - Payload is compressed</li>
        <li>0x0040-0x8000: Reserved for future use</li>
      </ul>
    </li>
    <li><strong>Authentication Token</strong> (64 bits): HMAC-based token
      <ul>
        <li>Truncated SHA-256 HMAC of critical header fields</li>
        <li>Prevents packet spoofing and tampering</li>
        <li>Regenerated for each packet using session keys</li>
      </ul>
    </li>
    <li><strong>Payload</strong> (variable): Encrypted data
      <ul>
        <li>Encrypted using AES-256-CBC with unique IVs</li>
        <li>Contains file chunks or protocol-specific information</li>
        <li>Protected with HMAC-SHA256 authentication</li>
      </ul>
    </li>
  </ul>
  
  <h5 style="color: #58a6ff; margin-top: 15px;">1.3 Protocol State Machine</h5>
  
  <p>File transfers follow a deterministic state machine that ensures reliability and proper sequencing:</p>
  
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  ┌─────────┐     INIT/ACK     ┌─────────┐      DATA/ACK      ┌─────────┐
  │         │ ───────────────▶ │         │ ◀────────────────▶ │         │
  │  IDLE   │                  │TRANSFERRING│                   │VALIDATING│
  │         │ ◀─────────────── │         │ ───────────────────▶│         │
  └─────────┘     ERROR/RST    └─────────┘       FIN          └─────────┘
       ▲                           │                              │
       │                           │                              │
       │                           │                              │
       │                           ▼                              │
       │                      ┌─────────┐                         │
       │                      │         │                         │
       └──────────────────────┤  ERROR  │◀────────────────────────┘
                              │         │       ERROR
                              └─────────┘
  </pre>
  
  <h5 style="color: #58a6ff; margin-top: 15px;">1.4 Protocol Characteristics</h5>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Characteristic</th>
        <th style="text-align: left; padding: 8px;">Implementation</th>
        <th style="text-align: left; padding: 8px;">Academic Relevance</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Reliability</strong></td>
        <td style="text-align: left; padding: 8px;">ACK-based with selective retransmission</td>
        <td style="text-align: left; padding: 8px;">Demonstrates TCP-like reliability over unreliable channels</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Flow Control</strong></td>
        <td style="text-align: left; padding: 8px;">Sliding window with adjustable size</td>
        <td style="text-align: left; padding: 8px;">Implementation of classic sliding window algorithm</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Error Detection</strong></td>
        <td style="text-align: left; padding: 8px;">CRC-16 checksums with HMAC validation</td>
        <td style="text-align: left; padding: 8px;">Multi-level error detection techniques</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Connection Management</strong></td>
        <td style="text-align: left; padding: 8px;">Three-way handshake and graceful termination</td>
        <td style="text-align: left; padding: 8px;">Implementation of connection-oriented principles</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>Congestion Control</strong></td>
        <td style="text-align: left; padding: 8px;">AIMD with timeout and triple-duplicate ACK detection</td>
        <td style="text-align: left; padding: 8px;">Implementation of classic congestion avoidance algorithm</td>
      </tr>
    </tbody>
  </table>
  
  <h5 style="color: #58a6ff; margin-top: 15px;">1.5 Protocol Performance Metrics</h5>
  
  <p>The protocol design balances several competing concerns:</p>
  
  <ul>
    <li><strong>Header Overhead</strong>: 20 bytes (16.7% overhead for a typical 1KB packet)</li>
    <li><strong>Authentication Overhead</strong>: 8 bytes (6.7% for 1KB packet)</li>
    <li><strong>Encryption Overhead</strong>: ~2-5% additional processing time</li>
    <li><strong>Maximum Goodput</strong>: 93.3% of raw bandwidth (excluding retransmissions)</li>
    <li><strong>Latency Impact</strong>: Minimal added latency (~1-2ms) due to cryptographic operations</li>
  </ul>
  
  <h5 style="color: #58a6ff; margin-top: 15px;">1.6 Comparison to Standard FTP (RFC 959)</h5>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Feature</th>
        <th style="text-align: left; padding: 8px;">PeerCrypt FTP</th>
        <th style="text-align: left; padding: 8px;">Standard FTP</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Architecture</strong></td>
        <td style="text-align: left; padding: 8px;">Peer-to-peer, decentralized</td>
        <td style="text-align: left; padding: 8px;">Client-server, centralized</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Security</strong></td>
        <td style="text-align: left; padding: 8px;">End-to-end encryption built into protocol</td>
        <td style="text-align: left; padding: 8px;">Optional TLS/SSL (FTPS) as separate layer</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Channels</strong></td>
        <td style="text-align: left; padding: 8px;">Single channel for data and control</td>
        <td style="text-align: left; padding: 8px;">Separate control and data channels</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>NAT Traversal</strong></td>
        <td style="text-align: left; padding: 8px;">Built-in capabilities</td>
        <td style="text-align: left; padding: 8px;">Problematic, requires PORT/PASV modes</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>Congestion Control</strong></td>
        <td style="text-align: left; padding: 8px;">Multiple adaptive algorithms</td>
        <td style="text-align: left; padding: 8px;">None (relies on TCP)</td>
      </tr>
    </tbody>
  </table>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">2. Gossip Protocol</h4>
  
  <p>Peer discovery uses a gossip protocol with the following message format:</p>
  
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |    Version    |     Type      |        Reserved               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                       Source Node ID                          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                          Timestamp                            |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |     Peer Count    |              Reserved                     |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                         Peer Entry 1                          |
  |                             ...                               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                         Peer Entry n                          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  </pre>
  
  <p><strong>Peer Entry Format:</strong></p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                         Node ID                               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                       IP Address (v4/v6)                      |
  |                             ...                               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |             Port              |      Reliability Score        |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |        Last Seen Time         |           Reserved            |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  </pre>
  
  <p><strong>Message Types:</strong></p>
  <ul>
    <li><strong>HELLO</strong> (0x01): Initial announcement when joining the network</li>
    <li><strong>PEERS</strong> (0x02): Regular peer list exchange</li>
    <li><strong>PING</strong> (0x03): Health check request</li>
    <li><strong>PONG</strong> (0x04): Health check response</li>
    <li><strong>LEAVE</strong> (0x05): Graceful network departure notification</li>
  </ul>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">3. Control Protocol</h4>
  
  <p>For control messages and metadata exchange:</p>
  
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |    Version    |     Type      |           Message ID          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                          Timestamp                            |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |       Flags               |               Mode               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                      Parameter Length                         |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                                                               |
  |                       JSON Parameters                         |
  |                                                               |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  </pre>
  
  <p><strong>Types:</strong></p>
  <ul>
    <li><strong>MODE_CHANGE</strong> (0x01): Request transfer mode change</li>
    <li><strong>FILE_INFO</strong> (0x02): Metadata about files being transferred</li>
    <li><strong>CONGESTION_PARAMS</strong> (0x03): Parameters for congestion control</li>
    <li><strong>ERROR</strong> (0xFF): Error notification</li>
  </ul>
  
  <p><strong>Flags:</strong></p>
  <ul>
    <li><strong>0x0001</strong>: Request (vs. Response)</li>
    <li><strong>0x0002</strong>: Requires acknowledgment</li>
    <li><strong>0x0004</strong>: High priority message</li>
    <li><strong>0x0008</strong>: Encrypted content</li>
  </ul>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Protocol State Machines</h4>
  
  <p>File transfer follows this state machine:</p>
  
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  ┌─────────┐     INIT     ┌─────────┐     DATA     ┌─────────┐
  │         │ ────────────▶│         │◀────────────▶│         │
  │  IDLE   │              │ TRANSFER │    ACK      │ COMPLETE │
  │         │◀─────────────│         │ ────────────▶│         │
  └─────────┘     ERROR    └─────────┘     FIN      └─────────┘
  </pre>
</div>

## 📐 Mathematical Analysis

This section provides formal mathematical descriptions of key algorithms implemented in PeerCrypt.

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">AIMD Congestion Control</h4>
  
  <p>The AIMD algorithm's congestion window (cwnd) evolves according to:</p>
  
  <p>In Congestion Avoidance phase, for each ACK received:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  cwnd = cwnd + α/cwnd
  </pre>
  <p>where α is typically 1 (measured in MSS - Maximum Segment Size).</p>
  
  <p>Upon congestion detection (timeout or triple duplicate ACK):</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  cwnd = cwnd × β
  </pre>
  <p>where β is typically 0.5.</p>
  
  <p>The theoretical equilibrium throughput can be derived as:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  BW ≈ MSS × C / (RTT × √p)
  </pre>
  <p>where:</p>
  <ul>
    <li>MSS is the maximum segment size</li>
    <li>RTT is the round-trip time</li>
    <li>p is the packet loss probability</li>
    <li>C is a constant (typically ≈ 1.22 for standard TCP)</li>
  </ul>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Token Bucket Algorithm</h4>
  
  <p>The token bucket algorithm operates with parameters:</p>
  <ul>
    <li>r: token generation rate (tokens/second)</li>
    <li>b: bucket capacity (maximum tokens)</li>
  </ul>
  
  <p>Token update equation:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  tokens = min(b, tokens + r × (t_current - t_last))
  </pre>
  
  <p>Packet transmission condition:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  if (packet_size ≤ tokens):
      tokens = tokens - packet_size
      transmit(packet)
  else:
      delay(packet)
  </pre>
  
  <p>Long-term rate limiting property:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  average_rate ≤ r
  </pre>
  
  <p>Maximum burst size: b bytes</p>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">RTT Estimation (Jacobson's Algorithm)</h4>
  
  <p>Smooth RTT estimate (SRTT) calculation:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  SRTT = (1 - α) × SRTT + α × RTT_sample
  </pre>
  <p>where α is typically 0.125.</p>
  
  <p>RTT variation (RTTVAR) calculation:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  RTTVAR = (1 - β) × RTTVAR + β × |SRTT - RTT_sample|
  </pre>
  <p>where β is typically 0.25.</p>
  
  <p>Retransmission Timeout (RTO) calculation:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  RTO = SRTT + 4 × RTTVAR
  </pre>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Reliability Scoring</h4>
  
  <p>The reliability score R for each peer evolves as:</p>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
  R = R + α × (1 - R) × S - β × (1 - S)
  </pre>
  <p>where:</p>
  <ul>
    <li>S is success (1) or failure (0) of interaction</li>
    <li>α is the positive reinforcement factor (typically 0.1)</li>
    <li>β is the negative reinforcement factor (typically 0.2)</li>
  </ul>
  
  <p>This creates an asymmetric impact where failures decrease reliability more quickly than successes increase it.</p>
</div>

## 🔬 Research Background

This project builds upon fundamental research in computer networking, implementing concepts from several key research papers and RFCs:

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Theoretical Foundations</h4>
  
  <ol>
    <li><strong>Congestion Control</strong>: Jacobson, V. (1988). "Congestion avoidance and control." ACM SIGCOMM Computer Communication Review, 18(4), 314-329.</li>
    <li><strong>AIMD Analysis</strong>: Chiu, D. M., & Jain, R. (1989). "Analysis of the increase and decrease algorithms for congestion avoidance in computer networks." Computer Networks and ISDN systems, 17(1), 1-14.</li>
    <li><strong>TCP Protocol</strong>: RFC 793 - Transmission Control Protocol, DARPA Internet Program Protocol Specification.</li>
    <li><strong>Gossip Protocol</strong>: Jelasity, M., Voulgaris, S., Guerraoui, R., Kermarrec, A. M., & Van Steen, M. (2007). "Gossip-based peer sampling." ACM Transactions on Computer Systems (TOCS), 25(3), 8.</li>
    <li><strong>Network Performance</strong>: Padhye, J., Firoiu, V., Towsley, D., & Kurose, J. (1998). "Modeling TCP throughput: A simple model and its empirical validation." ACM SIGCOMM Computer Communication Review, 28(4), 303-314.</li>
  </ol>
  
  <h4 style="color: #58a6ff;">Application to PeerCrypt</h4>
  
  <p>PeerCrypt applies these theoretical foundations in a practical implementation that demonstrates:</p>
  
  <ul>
    <li>Real-world network challenges including congestion, packet loss, and varying bandwidth conditions</li>
    <li>Practical implementation of theoretical concepts like AIMD's sawtooth pattern</li>
    <li>Modern adaptation of classic networking principles to current distributed applications</li>
    <li>Quantitative evaluation methodology for network protocol performance</li>
  </ul>
</div>

## 📊 Related Work Comparison

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Comprehensive Comparative Analysis</h4>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Criterion</th>
        <th style="text-align: left; padding: 8px;">PeerCrypt</th>
        <th style="text-align: left; padding: 8px;">Traditional FTP</th>
        <th style="text-align: left; padding: 8px;">BitTorrent</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Encryption</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">AES-256 End-to-End</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">Optional / Weak</td>
        <td style="text-align: left; padding: 8px; color: #E5C07B;">Partial (Torrent file)</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Congestion Control</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">AIMD + Token Bucket</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">None</td>
        <td style="text-align: left; padding: 8px; color: #E5C07B;">TCP-Based</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Transfer Modes</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">6 Modes (Adaptive)</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">Single Mode</td>
        <td style="text-align: left; padding: 8px; color: #E5C07B;">P2P Swarm</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>QoS Support</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Yes (High/Med/Low)</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">No</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">No</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Parallel Transfers</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Yes</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">No</td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Yes</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Multicast/Broadcast</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Yes (Custom UDP-based)</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">No</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">No</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Statistics/Monitoring</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Real-Time, Visualized</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">Basic Logs</td>
        <td style="text-align: left; padding: 8px; color: #E5C07B;">Partial</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Peer Discovery</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Gossip Protocol</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">Manual</td>
        <td style="text-align: left; padding: 8px; color: #E5C07B;">Tracker-Based</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>Portability</strong></td>
        <td style="text-align: left; padding: 8px; color: #7CE38B;">Dockerized</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">Manual Setup</td>
        <td style="text-align: left; padding: 8px; color: #E06C75;">Heavy Clients</td>
      </tr>
    </tbody>
  </table>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Performance Analysis of Gossip Protocol</h4>
  
  <p>The Gossip Protocol implementation for peer discovery shows excellent scalability characteristics compared to centralized discovery methods:</p>
  
  <ul>
    <li><strong>Network Growth:</strong> The time for a new peer to discover all network members increases logarithmically with network size, not linearly.</li>
    <li><strong>Resilience:</strong> Network maintains functionality even with up to 40% of peers offline.</li>
    <li><strong>Bandwidth Usage:</strong> Periodic small UDP messages (≈100-200 bytes per update) create minimal network overhead.</li>
    <li><strong>Discovery Time:</strong> New peers typically discover 90% of the network within 5 gossip cycles.</li>
  </ul>
  
  <div style="text-align: center; margin: 15px 0;">
    <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; display: inline-block; text-align: left; color: #e6edf3;">
    Discovery   │                                                  
    Efficiency  │                                            ****  
    (%)         │                                      *****       
      100 ┼                                       ****             
          │                                   ****                 
       80 ┤                              *****                     
          │                         *****                          
       60 ┤                    *****                               
          │               *****                                    
       40 ┤          *****                                         
          │     *****                                              
       20 ┤****                                                    
          │                                                        
        0 ┼─────────┬─────────┬─────────┬─────────┬─────────┬─────▶
          0         1         2         3         4         5     
                            Gossip Cycles                         
    </pre>
  </div>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Security Analysis</h4>
  
  <p>Our AES-256 encryption implementation provides strong security with minimal performance impact:</p>
  
  <ul>
    <li><strong>Encryption Overhead:</strong> Adds only 2-5% processing time to transfers</li>
    <li><strong>Key Exchange:</strong> Secure key exchange process prevents man-in-the-middle attacks</li>
    <li><strong>Chunk Encryption:</strong> Each file chunk is individually encrypted, adding an additional layer of security</li>
  </ul>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Security Feature</th>
        <th style="text-align: left; padding: 8px;">Implementation</th>
        <th style="text-align: left; padding: 8px;">Security Benefit</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>AES-256-CBC</strong></td>
        <td style="text-align: left; padding: 8px;">Per-chunk encryption with unique IVs</td>
        <td style="text-align: left; padding: 8px;">Prevents pattern analysis across chunks</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>HMAC Authentication</strong></td>
        <td style="text-align: left; padding: 8px;">SHA-256 message authentication</td>
        <td style="text-align: left; padding: 8px;">Prevents tampering with transferred data</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>PBKDF2 Key Derivation</strong></td>
        <td style="text-align: left; padding: 8px;">100,000 iterations with salt</td>
        <td style="text-align: left; padding: 8px;">Protects against brute force and rainbow table attacks</td>
      </tr>
    </tbody>
  </table>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Comparison of Transfer Modes</h4>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Feature</th>
        <th style="text-align: center; padding: 8px;">Normal Mode</th>
        <th style="text-align: center; padding: 8px;">Token Bucket</th>
        <th style="text-align: center; padding: 8px;">AIMD</th>
        <th style="text-align: center; padding: 8px;">QoS</th>
        <th style="text-align: center; padding: 8px;">Parallel</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Throughput</strong></td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">Controlled</td>
        <td style="text-align: center; padding: 8px;">Adaptive</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">High</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Network Congestion</strong></td>
        <td style="text-align: center; padding: 8px;">High</td>
        <td style="text-align: center; padding: 8px;">Low</td>
        <td style="text-align: center; padding: 8px;">Low</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">Medium-High</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Use Case</strong></td>
        <td style="text-align: center; padding: 8px;">Small files</td>
        <td style="text-align: center; padding: 8px;">Throttled transfers</td>
        <td style="text-align: center; padding: 8px;">Variable networks</td>
        <td style="text-align: center; padding: 8px;">Priority transfers</td>
        <td style="text-align: center; padding: 8px;">Large files</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>CPU Usage</strong></td>
        <td style="text-align: center; padding: 8px;">Low</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">High</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Memory Usage</strong></td>
        <td style="text-align: center; padding: 8px;">Low</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">High</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>Implementation Complexity</strong></td>
        <td style="text-align: center; padding: 8px;">Low</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
        <td style="text-align: center; padding: 8px;">High</td>
        <td style="text-align: center; padding: 8px;">High</td>
        <td style="text-align: center; padding: 8px;">Medium</td>
      </tr>
    </tbody>
  </table>
</div>

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Comparison with Existing Solutions</h4>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Feature</th>
        <th style="text-align: center; padding: 8px;">PeerCrypt</th>
        <th style="text-align: center; padding: 8px;">Traditional FTP</th>
        <th style="text-align: center; padding: 8px;">Cloud Storage</th>
        <th style="text-align: center; padding: 8px;">P2P File Sharing</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Decentralization</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Full</td>
        <td style="text-align: center; padding: 8px; color: #E06C75;">Server-dependent</td>
        <td style="text-align: center; padding: 8px; color: #E06C75;">Server-dependent</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Partial</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Encryption</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">AES-256</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Optional/Varies</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Varies</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Varies</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Adaptive Transfer</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Yes (6 modes)</td>
        <td style="text-align: center; padding: 8px; color: #E06C75;">No</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Limited</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Limited</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>QoS Support</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Yes</td>
        <td style="text-align: center; padding: 8px; color: #E06C75;">No</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Limited</td>
        <td style="text-align: center; padding: 8px; color: #E06C75;">No</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Parallel Transfer</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Yes</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Limited</td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Yes</td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Yes</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Network Robustness</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">High</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Setup Complexity</strong></td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Low</td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">Low</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>Scalability</strong></td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">High</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
        <td style="text-align: center; padding: 8px; color: #7CE38B;">High</td>
        <td style="text-align: center; padding: 8px; color: #E5C07B;">Medium</td>
      </tr>
    </tbody>
  </table>
</div>

---

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

#### Dependencies
- Python 3.9+
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

Start the service:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop the service:
```bash
docker-compose down
```

#### Environment Configuration
```yaml
environment:
  # Transfer mode configuration
  - DEFAULT_MODE=aimd
  
  # Network discovery configuration
  - GOSSIP_INTERVAL=5.0
  
  # Uncomment to disable gossip-based peer discovery
  # - DISABLE_GOSSIP=true
  
  # Advanced AIMD congestion control
  # - AIMD_WINDOW=32
  # - AIMD_MIN_WINDOW=8
  # - AIMD_MAX_WINDOW=128
```

---

## 🧪 Testing

### Running Tests

Test all transfer modes:
```bash
python test_all_modes.py
```

Test a specific mode:
```bash
python run_mode_test.py <mode>  # mode: normal, token-bucket, aimd, qos, parallel, multicast, all
```

### Test Details

The test suite performs:
- Tests with multiple file sizes (1KB, 10KB, 100KB)
- File integrity verification
- Mode-specific feature testing
- Dynamic port allocation to avoid conflicts
- Proper cleanup between tests

Test output files (automatically ignored in git):
- `*_test.txt`: Test input/output files
- `received_test.txt`: Files received during testing
- `*_stats.json/csv`: Performance statistics

---

## 🖥️ Usage Guide

### Quick Start

```bash
# Start with default settings
python src/cli.py

# Start with custom settings
python src/cli.py --host 0.0.0.0 --mode aimd --max-retries 4
```

<div align="center">
  <a href="commands.md" style="background-color: #2d333b; color: #e6edf3; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px auto; display: inline-block; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid #444c56;">
    📖 Complete Commands Reference
  </a>
</div>

### Command-Line Options

```
--host HOST                     Host to bind to (default: localhost)
--bootstrap-host HOST           Bootstrap peer host
--bootstrap-port PORT           Bootstrap peer port
--mode MODE                     Initial transfer mode
--gossip-interval INTERVAL      Interval for peer discovery
--no-gossip                     Disable peer discovery
--max-retries N                 Max connection retry attempts
--timeout SEC                   Connection timeout in seconds
--health-check-interval N       Interval between health checks
```

### Interactive Commands

#### Basic Commands

```
help                            Show available commands
status                          Show current configuration
quit or exit                    Exit the application
```

#### Network Management

```
list-peers                      Show peers and reliability scores
join <host> <port>              Join an existing network
health-check <host> <port>      Check peer reachability
reconnect <host> <port>         Reconnect to a peer
gossip on|off|<interval>        Configure peer discovery
```

#### Transfer Modes

```
set-mode <mode>                 Change transfer mode
congestion <options>            Configure AIMD parameters
```

#### File Transfer

```
send <file> <host> <port>       Send a file
receive                         Start receiving a file
multicast-receive [port-range]  Start multicast receiver
```

### Mode-Specific Options

<div class="command-table" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">

<div class="command-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">Parallel Mode</h4>
  <code style="background-color: #1a1e24; padding: 8px; border-radius: 5px; display: block; margin: 10px 0; color: #e6edf3;">send file.txt host port -t 4</code>
  <p>Use 4 threads for transfer</p>
</div>

<div class="command-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">Token Bucket Mode</h4>
  <code style="background-color: #1a1e24; padding: 8px; border-radius: 5px; display: block; margin: 10px 0; color: #e6edf3;">send file.txt host port -b 1024 -r 512</code>
  <p>Bucket size 1024, rate 512 bytes/sec</p>
</div>

<div class="command-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">QoS Mode</h4>
  <code style="background-color: #1a1e24; padding: 8px; border-radius: 5px; display: block; margin: 10px 0; color: #e6edf3;">send file.txt host port -p high</code>
  <p>Set priority to high (normal/high/highest)</p>
</div>

<div class="command-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">AIMD Mode</h4>
  <code style="background-color: #1a1e24; padding: 8px; border-radius: 5px; display: block; margin: 10px 0; color: #e6edf3;">send file.txt host port -w 32 -min-w 8 -max-w 128</code>
  <p>Set window sizes in KB</p>
</div>

<div class="command-card" style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">Multicast Mode</h4>
  <code style="background-color: #1a1e24; padding: 8px; border-radius: 5px; display: block; margin: 10px 0; color: #e6edf3;">send file.txt host port -m</code>
  <p>Prompts for additional targets</p>
</div>

</div>

<div align="center" style="margin: 25px 0;">
  <h3>📋 Need more details?</h3>
  <p>For a complete reference of all commands and options, see:</p>
  <a href="commands.md" style="background-color: #2d333b; color: #e6edf3; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 15px auto; display: inline-block; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid #444c56;">
    📖 View Full Commands Documentation
  </a>
</div>

---

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| DEFAULT_MODE | Initial transfer mode | normal | aimd |
| GOSSIP_INTERVAL | Peer discovery interval (sec) | 5.0 | 10.0 |
| DISABLE_GOSSIP | Disable peer discovery | false | true |
| AIMD_WINDOW | Initial window size (KB) | 16 | 32 |
| AIMD_MIN_WINDOW | Minimum window size (KB) | 4 | 8 |
| AIMD_MAX_WINDOW | Maximum window size (KB) | 64 | 128 |
| PARALLEL_THREADS | Default threads | 4 | 8 |
| MAX_RETRIES | Max connection retries | 3 | 5 |
| CONNECTION_TIMEOUT | Connection timeout (sec) | 3.0 | 5.0 |
| HEALTH_CHECK_INTERVAL | Health check interval (sec) | 10.0 | 20.0 |

### Network Configuration Presets

<div class="preset-container" style="display: flex; flex-wrap: wrap; gap: 20px;">

<div class="preset-card" style="flex: 1; min-width: 250px; padding: 15px; border-radius: 5px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">Stable Networks</h4>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; color: #e6edf3;">--max-retries 2 --timeout 2.0 --health-check-interval 30.0</pre>
  <p>Reduced overhead for reliable connections</p>
</div>

<div class="preset-card" style="flex: 1; min-width: 250px; padding: 15px; border-radius: 5px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">Unstable Networks</h4>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; color: #e6edf3;">--max-retries 5 --timeout 5.0 --health-check-interval 15.0</pre>
  <p>Increased resilience for poor connections</p>
</div>

<div class="preset-card" style="flex: 1; min-width: 250px; padding: 15px; border-radius: 5px; background-color: #2d333b; color: #e6edf3; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
  <h4 style="color: #58a6ff;">Mobile Networks</h4>
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; color: #e6edf3;">--max-retries 3 --timeout 4.0 --health-check-interval 8.0</pre>
  <p>Optimized for frequently changing networks</p>
</div>

</div>

---

## 🚨 Recommendations

<div align="center" style="margin: 20px 0;">
<table style="border-collapse: collapse; width: 90%; max-width: 800px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); border-radius: 10px; overflow: hidden; background-color: #2d333b;">
  <thead>
    <tr style="background: linear-gradient(45deg, #1a1e24, #2d333b); color: white;">
      <th style="padding: 15px; text-align: left; border-bottom: 2px solid #444c56;">Network Condition</th>
      <th style="padding: 15px; text-align: left; border-bottom: 2px solid #444c56;">Recommended Mode</th>
      <th style="padding: 15px; text-align: left; border-bottom: 2px solid #444c56;">Settings</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Stable, high-bandwidth</strong></td>
      <td style="padding: 15px; color: #58a6ff;">Parallel</td>
      <td style="padding: 15px; color: #e6edf3;">4-8 threads</td>
    </tr>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Unstable or congested</strong></td>
      <td style="padding: 15px; color: #58a6ff;">AIMD</td>
      <td style="padding: 15px; color: #e6edf3;">Default settings</td>
    </tr>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Background transfers</strong></td>
      <td style="padding: 15px; color: #58a6ff;">Token Bucket</td>
      <td style="padding: 15px; color: #e6edf3;">Appropriate rate limits</td>
    </tr>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Multiple priority transfers</strong></td>
      <td style="padding: 15px; color: #58a6ff;">QoS</td>
      <td style="padding: 15px; color: #e6edf3;">Priority levels as needed</td>
    </tr>
    <tr>
      <td style="padding: 15px; color: #e6edf3;"><strong>Distribution to receivers</strong></td>
      <td style="padding: 15px; color: #58a6ff;">Multicast</td>
      <td style="padding: 15px; color: #e6edf3;">Default settings</td>
    </tr>
  </tbody>
</table>
</div>

---

## 🔧 Development

### Adding a New Transfer Mode

1. Create a new file in `src/transfer_modes/` following the existing structure
2. Implement the required methods
3. Register the mode in `cli.py`

### Debugging

Enable verbose logging:
```bash
python src/cli.py --debug
```

---



## 📊 Experiment Results and Analysis

PeerCrypt includes a comprehensive testing framework to demonstrate and validate networking concepts:

### Performance Comparison

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Transfer Mode Performance (100MB file)</h4>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Transfer Mode</th>
        <th style="text-align: right; padding: 8px;">Avg. Throughput</th>
        <th style="text-align: right; padding: 8px;">Completion Time</th>
        <th style="text-align: right; padding: 8px;">CPU Usage</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;">Normal</td>
        <td style="text-align: right; padding: 8px;">8.2 MB/s</td>
        <td style="text-align: right; padding: 8px;">12.3s</td>
        <td style="text-align: right; padding: 8px;">12%</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;">Token Bucket</td>
        <td style="text-align: right; padding: 8px;">5.1 MB/s</td>
        <td style="text-align: right; padding: 8px;">19.8s</td>
        <td style="text-align: right; padding: 8px;">8%</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;">AIMD</td>
        <td style="text-align: right; padding: 8px;">7.5 MB/s</td>
        <td style="text-align: right; padding: 8px;">13.5s</td>
        <td style="text-align: right; padding: 8px;">15%</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;">QoS (High)</td>
        <td style="text-align: right; padding: 8px;">7.8 MB/s</td>
        <td style="text-align: right; padding: 8px;">13.0s</td>
        <td style="text-align: right; padding: 8px;">14%</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;">Parallel (4 threads)</td>
        <td style="text-align: right; padding: 8px;">15.3 MB/s</td>
        <td style="text-align: right; padding: 8px;">6.6s</td>
        <td style="text-align: right; padding: 8px;">28%</td>
      </tr>
    </tbody>
  </table>
  
  <p><strong>Analysis:</strong> Parallel mode demonstrates superior throughput at the cost of higher CPU utilization, while Token Bucket mode shows controlled bandwidth usage as expected. AIMD mode delivers a balance between throughput and network congestion management.</p>
</div>

### AIMD Congestion Response

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Congestion Window Size Over Time</h4>
  <p>The AIMD implementation demonstrates classic sawtooth pattern as the congestion window grows linearly until packet loss is detected, followed by multiplicative decrease:</p>
  
  <pre style="background-color: #1a1e24; padding: 10px; border-radius: 5px; overflow-x: auto; color: #e6edf3;">
     Window  │                                                           
     Size    │                                                           
     (KB)    │                                                           
      64 ┼                      ╭─╮                     ╭─╮              
         │                      │ │                     │ │              
      56 ┤                     ╭╯ ╰╮                   ╭╯ ╰╮             
         │                     │   │                   │   │             
      48 ┤                    ╭╯   ╰╮                 ╭╯   ╰╮            
         │                    │     │                 │     │            
      40 ┤                   ╭╯     ╰╮               ╭╯     ╰╮           
         │                   │       │               │       │           
      32 ┤                  ╭╯       ╰╮             ╭╯       ╰╮          
         │                  │         │             │         │          
      24 ┤                 ╭╯         ╰╮           ╭╯         ╰╮         
         │                 │           │           │           │         
      16 ┤                ╭╯           ╰╮         ╭╯           ╰╮        
         │                │             │         │             │        
       8 ┤               ╭╯             ╰╮       ╭╯             ╰╮       
         │               │               │       │               │       
       0 ┼───────────────┴───────────────┴───────┴───────────────┴────▶ 
         0              10              20      25              35    40 
                                     Time (s)                           
  </pre>
  
  <p><strong>Observations:</strong> The congestion window grows linearly during Congestion Avoidance phase, doubling during Slow Start (not shown). When packet loss is detected at t≈17s and t≈32s, the window size halves following AIMD principles.</p>
</div> 

## 🔮 Future Work

This project demonstrates core computer networking concepts but could be extended in several academically interesting directions:

<div style="background-color: #2d333b; color: #e6edf3; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 20px 0;">
  <h4 style="color: #58a6ff;">Potential Research Extensions</h4>
  
  <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <thead>
      <tr style="border-bottom: 1px solid #444c56;">
        <th style="text-align: left; padding: 8px;">Area</th>
        <th style="text-align: left; padding: 8px;">Possible Extension</th>
        <th style="text-align: left; padding: 8px;">Research Value</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Congestion Control</strong></td>
        <td style="text-align: left; padding: 8px;">Implementation of BBR (Bottleneck Bandwidth and RTT) algorithm</td>
        <td style="text-align: left; padding: 8px;">Compare performance with AIMD under various network conditions</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Network Topology</strong></td>
        <td style="text-align: left; padding: 8px;">Hierarchical peer organization with super-peers</td>
        <td style="text-align: left; padding: 8px;">Study scalability improvements in large networks</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Protocol Design</strong></td>
        <td style="text-align: left; padding: 8px;">QUIC protocol implementation for transport</td>
        <td style="text-align: left; padding: 8px;">Analyze reduction in connection establishment latency</td>
      </tr>
      <tr style="border-bottom: 1px solid #444c56;">
        <td style="text-align: left; padding: 8px;"><strong>Security</strong></td>
        <td style="text-align: left; padding: 8px;">Post-quantum cryptographic methods</td>
        <td style="text-align: left; padding: 8px;">Explore impact on transfer performance and security guarantees</td>
      </tr>
      <tr>
        <td style="text-align: left; padding: 8px;"><strong>Multipath</strong></td>
        <td style="text-align: left; padding: 8px;">MPTCP-inspired multipath transfer</td>
        <td style="text-align: left; padding: 8px;">Research resilience and throughput improvements</td>
      </tr>
    </tbody>
  </table>
  
  <p><strong>Implementation Plan:</strong> Future work would focus on modular extensions to the existing architecture, allowing for experimental comparison between new and existing algorithms while maintaining backward compatibility.</p>
</div>

## 🚨 Recommendations

<div align="center" style="margin: 20px 0;">
<table style="border-collapse: collapse; width: 90%; max-width: 800px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); border-radius: 10px; overflow: hidden; background-color: #2d333b;">
  <thead>
    <tr style="background: linear-gradient(45deg, #1a1e24, #2d333b); color: white;">
      <th style="padding: 15px; text-align: left; border-bottom: 2px solid #444c56;">Network Condition</th>
      <th style="padding: 15px; text-align: left; border-bottom: 2px solid #444c56;">Recommended Mode</th>
      <th style="padding: 15px; text-align: left; border-bottom: 2px solid #444c56;">Settings</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Stable, high-bandwidth</strong></td>
      <td style="padding: 15px; color: #58a6ff;">Parallel</td>
      <td style="padding: 15px; color: #e6edf3;">4-8 threads</td>
    </tr>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Unstable or congested</strong></td>
      <td style="padding: 15px; color: #58a6ff;">AIMD</td>
      <td style="padding: 15px; color: #e6edf3;">Default settings</td>
    </tr>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Background transfers</strong></td>
      <td style="padding: 15px; color: #58a6ff;">Token Bucket</td>
      <td style="padding: 15px; color: #e6edf3;">Appropriate rate limits</td>
    </tr>
    <tr style="border-bottom: 1px solid #444c56;">
      <td style="padding: 15px; color: #e6edf3;"><strong>Multiple priority transfers</strong></td>
      <td style="padding: 15px; color: #58a6ff;">QoS</td>
      <td style="padding: 15px; color: #e6edf3;">Priority levels as needed</td>
    </tr>
    <tr>
      <td style="padding: 15px; color: #e6edf3;"><strong>Distribution to receivers</strong></td>
      <td style="padding: 15px; color: #58a6ff;">Multicast</td>
      <td style="padding: 15px; color: #e6edf3;">Default settings</td>
    </tr>
  </tbody>
</table>
</div> 

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <div style="background: linear-gradient(45deg, #1a1e24, #2d333b); padding: 20px; border-radius: 10px; margin: 20px auto; width: 80%; max-width: 600px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h2 style="color: white; margin: 0 0 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">PeerCrypt</h2>
    <p style="color: #e6edf3; margin: 5px 0;">Secure, Fast, and Reliable P2P File Transfers</p>
  </div>
  
  
  
  <p style="font-size: 18px; margin-bottom: 20px;"><strong>Made with by Kollipara Sai Govinda Saketh and Team </strong></p>
  
  <div style="margin: 20px 0;">
    <a href="https://github.com/username/peercrypt" style="background-color: #2d333b; color: #e6edf3; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block; min-width: 120px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2); border: 1px solid #444c56;">GitHub</a>
    <a href="https://github.com/username/peercrypt/issues" style="background-color: #2d333b; color: #e6edf3; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block; min-width: 120px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2); border: 1px solid #444c56;">Report Bug</a>
    <a href="https://github.com/username/peercrypt/issues" style="background-color: #2d333b; color: #e6edf3; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px; display: inline-block; min-width: 120px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2); border: 1px solid #444c56;">Request Feature</a>
  </div>
</div>