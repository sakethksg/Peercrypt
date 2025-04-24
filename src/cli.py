import argparse
import sys
import os
import socket
import time
import json
from typing import Optional, List, Tuple
from colorama import init, Fore, Style
try:
    import readline  # For Unix-like systems
except ImportError:
    import pyreadline3 as readline  # For Windows
from transfer_modes.normal_mode import NormalMode
from transfer_modes.token_bucket_mode import TokenBucketMode
from transfer_modes.aimd_mode import AIMDMode
from transfer_modes.qos_mode import QoSMode
from transfer_modes.parallel_mode import ParallelMode
from transfer_modes.multicast_mode import MulticastMode
from network.peer_discovery import PeerDiscovery

def is_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

class FileTransferCLI:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.peer_discovery = PeerDiscovery(host, port)
        self.transfer_modes = {
            'normal': NormalMode(host, port),
            'token-bucket': TokenBucketMode(host, port, bucket_size=1024, token_rate=100),
            'aimd': AIMDMode(host, port),
            'qos': QoSMode(host, port),
            'parallel': ParallelMode(host, port, num_threads=4),
            'multicast': MulticastMode(host, port)
        }
        self.current_mode = 'normal'
        self.total_bytes_transferred = 0
        self.successful_transfers = 0
        self.failed_transfers = 0

    def print_status(self):
        """Print current status and statistics."""
        print(f"\n{Fore.CYAN}=== Current Status ==={Style.RESET_ALL}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Current Mode: {Fore.GREEN}{self.current_mode}{Style.RESET_ALL}")
        print(f"Total Data Transferred: {self.total_bytes_transferred / 1024:.2f} KB")
        print(f"Successful Transfers: {Fore.GREEN}{self.successful_transfers}{Style.RESET_ALL}")
        print(f"Failed Transfers: {Fore.RED}{self.failed_transfers}{Style.RESET_ALL}")

    def start(self):
        """Start the peer discovery service."""
        self.peer_discovery.start()
        print(f"{Fore.GREEN}Started peer discovery service on {self.host}:{self.port}{Style.RESET_ALL}")

    def stop(self):
        """Stop the peer discovery service."""
        self.peer_discovery.stop()
        print(f"{Fore.YELLOW}Stopped peer discovery service{Style.RESET_ALL}")

    def join_network(self, bootstrap_host: str, bootstrap_port: int) -> bool:
        """Join the network using a bootstrap peer."""
        success = self.peer_discovery.join_network(bootstrap_host, bootstrap_port)
        if success:
            print(f"{Fore.GREEN}Successfully joined network via {bootstrap_host}:{bootstrap_port}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Failed to join network via {bootstrap_host}:{bootstrap_port}{Style.RESET_ALL}")
        return success

    def list_peers(self):
        """List all active peers in the network."""
        active_peers = self.peer_discovery.get_active_peers()
        
        print(f"\n{Fore.CYAN}=== Peer Network Status ==={Style.RESET_ALL}")
        if not active_peers:
            print(f"{Fore.YELLOW}No active peers found{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}Active peers: {len(active_peers)}{Style.RESET_ALL}")
            for i, (host, port) in enumerate(active_peers):
                print(f"  {i+1}. {host}:{port}")
        
        # Get reliable peers with reliability scores
        reliable_peers = self.peer_discovery.get_reliable_peers(min_reliability=0.5)
        if reliable_peers:
            print(f"\n{Fore.GREEN}Most reliable peers:{Style.RESET_ALL}")
            for i, (host, port, reliability) in enumerate(reliable_peers[:5]):  # Show top 5
                reliability_percent = int(reliability * 100)
                reliability_color = Fore.GREEN if reliability_percent > 80 else Fore.YELLOW if reliability_percent > 50 else Fore.RED
                print(f"  {i+1}. {host}:{port} - Reliability: {reliability_color}{reliability_percent}%{Style.RESET_ALL}")
        
        # Add gossip protocol status
        print(f"\n{Fore.CYAN}=== Gossip Protocol Status ==={Style.RESET_ALL}")
        if hasattr(self.peer_discovery, 'running') and self.peer_discovery.running:
            print(f"Status: {Fore.GREEN}Active{Style.RESET_ALL}")
            print(f"Gossip interval: {self.peer_discovery.gossip_interval} seconds")
            print(f"Total known peers (including inactive): {len(self.peer_discovery.peers)}")
            
            # Show inactive peers
            inactive_peers = set()
            current_time = time.time()
            with self.peer_discovery.lock:
                for peer_id, peer in self.peer_discovery.peers.items():
                    if peer.status == 'inactive':
                        inactive_peers.add((peer.host, peer.port, peer.last_seen, peer.failed_attempts))
            
            if inactive_peers:
                print(f"\n{Fore.YELLOW}Inactive peers: {len(inactive_peers)}{Style.RESET_ALL}")
                for i, (host, port, last_seen, failed_attempts) in enumerate(inactive_peers):
                    time_ago = int(current_time - last_seen)
                    print(f"  {i+1}. {host}:{port} (last seen {time_ago} seconds ago, {failed_attempts} failed attempts)")
        else:
            print(f"Status: {Fore.RED}Inactive{Style.RESET_ALL}")
            print(f"Use 'gossip on' to enable gossip-based peer discovery")

    def set_mode(self, mode: str):
        """Set the current transfer mode."""
        if mode not in self.transfer_modes:
            print(f"{Fore.RED}Invalid mode: {mode}{Style.RESET_ALL}")
            print(f"Available modes: {', '.join(self.transfer_modes.keys())}")
            return
        self.current_mode = mode
        print(f"{Fore.GREEN}Set transfer mode to: {mode}{Style.RESET_ALL}")

    def send_file(self, filepath: str, target_host: str, target_port: int, **kwargs):
        """Send a file to a peer"""
        try:
            if not os.path.exists(filepath):
                print(f"Error: File '{filepath}' does not exist")
                return

            file_size = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            # Verify target is reachable
            peer_id = f"{target_host}:{target_port}"
            with self.peer_discovery.lock:
                if peer_id in self.peer_discovery.peers:
                    peer = self.peer_discovery.peers[peer_id]
                    if peer.status == 'inactive':
                        print(f"{Fore.YELLOW}Warning: Peer {target_host}:{target_port} was previously marked as inactive.{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Attempting to reconnect...{Style.RESET_ALL}")
                        # Try to perform a health check
                        health_check_successful = self._check_peer_health(target_host, target_port)
                        if not health_check_successful:
                            print(f"{Fore.RED}Could not reach peer {target_host}:{target_port}. Transfer may fail.{Style.RESET_ALL}")
                            proceed = input(f"{Fore.YELLOW}Proceed with transfer anyway? (y/n): {Style.RESET_ALL}").lower()
                            if proceed != 'y':
                                return
            
            # Display transfer parameters
            print("\nTransfer Parameters:")
            print(f"File: {filename}")
            print(f"Size: {file_size / 1024:.2f} KB")
            
            # Handle multicast mode
            if self.current_mode == "multicast":
                # Get targets list or use single target
                targets = kwargs.get('targets', [(target_host, target_port)])
                print(f"Mode: Multicast")
                print(f"Number of targets: {len(targets)}")
                
                # Verify all targets are reachable
                unreachable_targets = []
                for host, port in targets:
                    if not self._check_peer_health(host, port):
                        unreachable_targets.append((host, port))
                
                if unreachable_targets:
                    print(f"{Fore.YELLOW}Warning: {len(unreachable_targets)} target(s) appear to be unreachable:{Style.RESET_ALL}")
                    for host, port in unreachable_targets:
                        print(f"  - {host}:{port}")
                    proceed = input(f"{Fore.YELLOW}Proceed with transfer to remaining targets? (y/n): {Style.RESET_ALL}").lower()
                    if proceed != 'y':
                        return
                    # Filter out unreachable targets
                    targets = [t for t in targets if t not in unreachable_targets]
                    if not targets:
                        print(f"{Fore.RED}No reachable targets remaining. Aborting transfer.{Style.RESET_ALL}")
                        return
                
                for i, (host, port) in enumerate(targets):
                    print(f"Target {i+1}: {host}:{port}")
                
                print("\nStarting multicast transfer...")
                success = self.transfer_modes[self.current_mode].send_file(filepath, targets)
                
                if success:
                    print(f"\n{Fore.GREEN}Multicast transfer successful{Style.RESET_ALL}")
                    self.successful_transfers += 1
                    self.total_bytes_transferred += file_size
                else:
                    print(f"\n{Fore.RED}Multicast transfer failed{Style.RESET_ALL}")
                    self.failed_transfers += 1
                return
            
            # For non-multicast modes
            print(f"Target: {target_host}:{target_port}")
            
            # Display mode-specific parameters
            if self.current_mode == "token-bucket":
                bucket_size = kwargs.get('bucket_size', 1024)
                token_rate = kwargs.get('token_rate', 100)
                print(f"Mode: Token Bucket")
                print(f"Bucket Size: {bucket_size} tokens")
                print(f"Token Rate: {token_rate} tokens/sec")
                print(f"Estimated Rate: {token_rate} KB/s")
            elif self.current_mode == "qos":
                priority = kwargs.get('priority', 'normal')
                print(f"Mode: QoS")
                print(f"Priority: {priority}")
            elif self.current_mode == "parallel":
                num_threads = kwargs.get('num_threads', 2)
                print(f"Mode: Parallel")
                print(f"Threads: {num_threads}")
            elif self.current_mode == "aimd":
                print(f"Mode: AIMD")
                print("Using adaptive congestion control")
            else:
                print(f"Mode: Normal")
            
            print("\nStarting transfer...")
            success = self.transfer_modes[self.current_mode].send_file(filepath, target_host, target_port, **kwargs)
            
            if success:
                print("\nTransfer Statistics:")
                if hasattr(self.transfer_modes[self.current_mode], 'stats'):
                    stats = self.transfer_modes[self.current_mode].stats.get_stats()
                    print(f"Duration: {stats['duration']:.2f} seconds")
                    print(f"Average Rate: {stats['average_rate']:.2f} KB/s")
                    print(f"Chunks Sent: {stats['chunks_sent']}")
                    print(f"Retries: {stats['retries']}")
                    print(f"Errors: {stats['errors']}")
                    print(f"\nDetailed statistics saved to transfer_stats_{filename}.json")
                self.successful_transfers += 1
                self.total_bytes_transferred += file_size
                
                # Update peer reliability after successful transfer
                with self.peer_discovery.lock:
                    peer_id = f"{target_host}:{target_port}"
                    if peer_id in self.peer_discovery.peers:
                        self.peer_discovery.peers[peer_id].reliability = min(1.0, self.peer_discovery.peers[peer_id].reliability + 0.1)
            else:
                print("Transfer failed")
                self.failed_transfers += 1
                
                # Update peer reliability after failed transfer
                with self.peer_discovery.lock:
                    peer_id = f"{target_host}:{target_port}"
                    if peer_id in self.peer_discovery.peers:
                        self.peer_discovery.peers[peer_id].failed_attempts += 1
                        self.peer_discovery.peers[peer_id].reliability = max(0.1, self.peer_discovery.peers[peer_id].reliability - 0.2)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.failed_transfers += 1

    def receive_file(self):
        """Receive a file from a peer"""
        try:
            print("\nWaiting for incoming file...")
            print(f"Listening on {self.host}:{self.port}")
            print(f"Current Mode: {self.current_mode}")
            
            if self.current_mode == "token-bucket":
                print("Token Bucket Parameters:")
                print(f"Bucket Size: {self.transfer_modes[self.current_mode].bucket.capacity} tokens")
                print(f"Token Rate: {self.transfer_modes[self.current_mode].bucket.rate} tokens/sec")
            elif self.current_mode == "parallel":
                print("Parallel Mode Active")
                print("Ready to receive multiple connections")
            elif self.current_mode == "multicast":
                print("Multicast Mode Active")
            
            success, filename = self.transfer_modes[self.current_mode].receive_file()
            
            if success:
                print("\nTransfer Statistics:")
                if hasattr(self.transfer_modes[self.current_mode], 'stats'):
                    stats = self.transfer_modes[self.current_mode].stats.get_stats()
                    print(f"Duration: {stats['duration']:.2f} seconds")
                    print(f"Average Rate: {stats['average_rate']:.2f} KB/s")
                    print(f"Chunks Received: {stats['chunks_sent']}")
                    print(f"Retries: {stats['retries']}")
                    print(f"Errors: {stats['errors']}")
                    print(f"\nDetailed statistics saved to transfer_stats_{filename}.json")
                print(f"\nFile received successfully: {filename}")
            else:
                print("Transfer failed")
            
        except Exception as e:
            print(f"Error: {str(e)}")

    def show_status(self):
        """Show detailed status information and available commands."""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════╗")
        print(f"║             PeerCrypt Status                 ║")
        print(f"╚══════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        self.print_status()
        
        # Calculate the number of peers with connection issues
        problematic_peers = 0
        with self.peer_discovery.lock:
            for peer_id, peer in self.peer_discovery.peers.items():
                if peer.status == 'inactive' or peer.failed_attempts > 0:
                    problematic_peers += 1
        
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════╗")
        print(f"║             Network Status                   ║")
        print(f"╚══════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"Peer Discovery: {'Active' if self.peer_discovery.running else 'Inactive'}")
        print(f"Gossip Interval: {self.peer_discovery.gossip_interval} seconds")
        print(f"Connection Timeout: {self.peer_discovery.timeout} seconds")
        print(f"Max Retries: {self.peer_discovery.max_retries}")
        
        active_peers = self.peer_discovery.get_active_peers()
        print(f"Active Peers: {len(active_peers)}")
        print(f"Problem Peers: {Fore.YELLOW if problematic_peers > 0 else Fore.GREEN}{problematic_peers}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════╗")
        print(f"║             Available Commands               ║")
        print(f"╚══════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        commands = [
            ("status", "Show this status information"),
            ("list-peers", "List all discovered peers"),
            ("set-mode <mode>", "Set transfer mode (normal|token-bucket|aimd|qos|parallel|multicast)"),
            ("send <file> <host> <port> [options]", "Send a file to a peer"),
            ("receive", "Start receiving a file"),
            ("health-check <host> <port>", "Check if a peer is reachable"),
            ("reconnect <host> <port>", "Attempt to reconnect to a peer"),
            ("gossip [on|off|interval]", "Configure gossip protocol settings"),
            ("congestion [options]", "Configure AIMD congestion control"),
            ("multicast-receive [port-range]", "Start multicast receiver"),
            ("exit", "Exit the application")
        ]
        
        for cmd, desc in commands:
            print(f"{Fore.GREEN}{cmd}{Style.RESET_ALL}: {desc}")

    def start_multicast_receiver(self, port_range=10):
        """Start a multicast receiver that listens on multiple ports"""
        try:
            # Ensure we're in multicast mode
            if self.current_mode != "multicast":
                print(f"{Fore.YELLOW}Switching to multicast mode for multicast receiver{Style.RESET_ALL}")
                self.set_mode("multicast")
                
            print(f"\n{Fore.CYAN}Starting multicast receiver on {self.host}...{Style.RESET_ALL}")
            print(f"Base port: {self.port}")
            print(f"Port range: {port_range} (will listen on ports {self.port}-{self.port+port_range-1})")
            print(f"{Fore.YELLOW}Press Ctrl+C to stop receiving{Style.RESET_ALL}")
            
            # Start the multicast receiver
            self.transfer_modes["multicast"].start_multicast_receiver(port_range)
            
        except Exception as e:
            print(f"{Fore.RED}Error starting multicast receiver: {str(e)}{Style.RESET_ALL}")

    def configure_gossip(self, interval=None, enable=True):
        """Configure or toggle the gossip-based peer discovery"""
        try:
            if enable:
                if interval is not None:
                    # Update the gossip interval
                    self.peer_discovery.gossip_interval = float(interval)
                    print(f"{Fore.GREEN}Gossip interval set to {interval} seconds{Style.RESET_ALL}")
                
                # Ensure gossip is running
                if not self.peer_discovery.running:
                    self.peer_discovery.start()
                    print(f"{Fore.GREEN}Gossip-based peer discovery enabled{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}Gossip-based peer discovery is already running{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Gossip interval: {self.peer_discovery.gossip_interval} seconds{Style.RESET_ALL}")
            else:
                # Disable gossip
                if self.peer_discovery.running:
                    self.peer_discovery.stop()
                    print(f"{Fore.YELLOW}Gossip-based peer discovery disabled{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Gossip-based peer discovery is already disabled{Style.RESET_ALL}")
                    
            # Show current peers from gossip
            active_peers = self.peer_discovery.get_active_peers()
            print(f"\n{Fore.CYAN}Current peers from gossip: {len(active_peers)}{Style.RESET_ALL}")
            for i, (host, port) in enumerate(active_peers):
                print(f"  {i+1}. {host}:{port}")
                
        except Exception as e:
            print(f"{Fore.RED}Error configuring gossip: {str(e)}{Style.RESET_ALL}")

    def configure_aimd(self, **kwargs):
        """Configure AIMD congestion control parameters"""
        try:
            if self.current_mode != "aimd":
                prev_mode = self.current_mode
                print(f"{Fore.YELLOW}Switching to AIMD mode to configure congestion control{Style.RESET_ALL}")
                self.set_mode("aimd")
                
            # Configure AIMD parameters
            config = self.transfer_modes["aimd"].configure(**kwargs)
            
            # Display the configuration
            print(f"\n{Fore.CYAN}=== AIMD Congestion Control Configuration ==={Style.RESET_ALL}")
            print(f"Window size: {config['initial_window']//1024} KB")
            print(f"Min window: {config['min_window']//1024} KB")
            print(f"Max window: {config['max_window']//1024} KB")
            print(f"Timeout detection: {Fore.GREEN if config['timeout_enabled'] else Fore.RED}{config['timeout_enabled']}{Style.RESET_ALL}")
            print(f"Triple DupACK detection: {Fore.GREEN if config['dupack_enabled'] else Fore.RED}{config['dupack_enabled']}{Style.RESET_ALL}")
            print(f"DupACK threshold: {config['dup_ack_threshold']}")
            
            # Explanation of congestion detection mechanisms
            print(f"\n{Fore.CYAN}=== Congestion Detection Mechanisms ==={Style.RESET_ALL}")
            print(f"1. {Fore.GREEN}Timeout-based detection:{Style.RESET_ALL}")
            print(f"   Detects packet loss when ACKs aren't received within the retransmission timeout (RTO)")
            print(f"   RTO is calculated dynamically based on measured round-trip times")
            print(f"   When a timeout occurs, the window size is reduced by half (multiplicative decrease)")
            
            print(f"\n2. {Fore.GREEN}Triple duplicate ACK detection:{Style.RESET_ALL}")
            print(f"   Detects packet loss when receiving the same ACK multiple times")
            print(f"   After receiving {config['dup_ack_threshold']} duplicate ACKs, fast retransmit is triggered")
            print(f"   This allows quicker recovery than waiting for a timeout")
            
            # Provide usage examples
            print(f"\n{Fore.CYAN}=== Examples ==={Style.RESET_ALL}")
            print(f"• Configure via dedicated command:")
            print(f"  congestion window 8 timeout on dupack on")
            print(f"  congestion min-window 2 max-window 32 threshold 4")
            
            print(f"\n• Configure when sending:")
            print(f"  send file.txt 192.168.1.100 5000 -w 4 -no-timeout")
            print(f"  send large-file.dat 192.168.1.100 5000 -w 16 -min-w 2 -max-w 32")
            print(f"  send important.pdf 192.168.1.100 5000 -no-dupack -ack-threshold 4")
            
        except Exception as e:
            print(f"{Fore.RED}Error configuring AIMD: {str(e)}{Style.RESET_ALL}")

    def _check_peer_health(self, host: str, port: int) -> bool:
        """Check if a peer is reachable and healthy."""
        try:
            # Create a temporary socket for health check
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(3.0)  # Short timeout for health check
                
                # Send health check message
                message = {
                    'type': 'health_check',
                    'source': {'host': self.host, 'port': self.port},
                    'timestamp': time.time()
                }
                s.sendto(json.dumps(message).encode(), (host, port))
                
                # Wait for response
                try:
                    data, _ = s.recvfrom(65535)
                    response = json.loads(data.decode())
                    
                    if response.get('type') == 'health_check_ack':
                        # Update peer in our list
                        with self.peer_discovery.lock:
                            peer_id = f"{host}:{port}"
                            if peer_id in self.peer_discovery.peers:
                                self.peer_discovery.peers[peer_id].status = 'active'
                                self.peer_discovery.peers[peer_id].last_seen = time.time()
                                self.peer_discovery.peers[peer_id].failed_attempts = 0
                            else:
                                # Add peer if not in our list
                                self.peer_discovery._update_peer(host, port)
                        return True
                    return False
                except socket.timeout:
                    return False
        except Exception as e:
            print(f"{Fore.RED}Error checking peer health: {e}{Style.RESET_ALL}")
            return False

    # Add a new command to force health check on specific peer
    def health_check_peer(self, host: str, port: int):
        """Perform a health check on a specific peer."""
        print(f"Performing health check on {host}:{port}...")
        
        if self._check_peer_health(host, port):
            print(f"{Fore.GREEN}Peer {host}:{port} is healthy and responding.{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Peer {host}:{port} is not responding.{Style.RESET_ALL}")
            return False

def main():
    init()
    # Setup command history
    readline.parse_and_bind('tab: complete')
    
    from colorama import Fore, Style
    print(f"\n{Fore.CYAN}{'═'*94}")
    print(f"{Fore.LIGHTCYAN_EX}  ██████╗ ███████╗███████╗██████╗  ██████╗██████╗ ██╗   ██╗██████╗ ████████╗      ")
    print(f"{Fore.LIGHTCYAN_EX}  ██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝      ")
    print(f"{Fore.LIGHTCYAN_EX}  ██████╔╝█████╗  █████╗  ██████╔╝██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║         ")
    print(f"{Fore.LIGHTCYAN_EX}  ██╔═══╝ ██╔══╝  ██╔══╝  ██╔══██╗██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║         ")
    print(f"{Fore.LIGHTCYAN_EX}  ██║     ███████╗███████╗██║  ██║╚██████╗██║  ██║   ██║   ██║        ██║         ")
    print(f"{Fore.LIGHTCYAN_EX}  ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝         ")
    print(f"{' '*92}")
    print(f"                       Decentralized File Transfer                                ")
    print(f"{' '*92}")
    print(f"  {Fore.MAGENTA}Developed by:                                                                  ")
    print(f"   {Fore.MAGENTA}• Saketh                                     ")
    print(f"   {Fore.MAGENTA}• Pavan                                             ")
    print(f"   {Fore.MAGENTA}• Naina                                                  ")
    print(f"{Fore.CYAN}{'═'*94}{Style.RESET_ALL}\n")


    
    parser = argparse.ArgumentParser(description="Decentralized File Transfer Application")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--bootstrap-host", help="Bootstrap peer host")
    parser.add_argument("--bootstrap-port", type=int, help="Bootstrap peer port")
    parser.add_argument("--mode", default="normal", choices=["normal", "token-bucket", "aimd", "qos", "parallel", "multicast"],
                      help="Initial transfer mode")
    parser.add_argument("--gossip-interval", type=float, default=5.0, 
                      help="Interval in seconds for gossip-based peer discovery (default: 5.0)")
    parser.add_argument("--no-gossip", action="store_true", 
                      help="Disable gossip-based peer discovery on startup")
    
    args = parser.parse_args()
    
    # Ask for port number
    while True:
        try:
            port = input(f"{Fore.YELLOW}Enter port number (1024-65535): {Style.RESET_ALL}")
            port = int(port)
            if 1024 <= port <= 65535:
                if is_port_available(port):
                    break
                else:
                    print(f"{Fore.RED}Port {port} is already in use. Please choose another port.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Port must be between 1024 and 65535{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
    
    cli = FileTransferCLI(args.host, port)
    cli.set_mode(args.mode)  # Set initial mode
    
    # Configure gossip settings from command line args
    if args.no_gossip:
        cli.configure_gossip(enable=False)
    else:
        cli.configure_gossip(interval=args.gossip_interval, enable=True)
        
    cli.start()
    
    if args.bootstrap_host and args.bootstrap_port:
        cli.join_network(args.bootstrap_host, args.bootstrap_port)
    
    print(f"\n{Fore.CYAN}Type 'help' for available commands{Style.RESET_ALL}")
    
    try:
        while True:
            try:
                command = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip().split()
                if not command:
                    continue
                    
                cmd = command[0].lower()
                
                if cmd == "help":
                    cli.show_status()
                
                elif cmd == "status":
                    cli.show_status()
                
                elif cmd == "list-peers":
                    cli.list_peers()
                
                elif cmd == "set-mode":
                    if len(command) != 2:
                        print(f"{Fore.RED}Usage: set-mode <mode>{Style.RESET_ALL}")
                        continue
                    cli.set_mode(command[1])
                
                elif cmd == "health-check":
                    if len(command) != 3:
                        print(f"{Fore.RED}Usage: health-check <host> <port>{Style.RESET_ALL}")
                        continue
                    try:
                        port = int(command[2])
                        cli.health_check_peer(command[1], port)
                    except ValueError:
                        print(f"{Fore.RED}Invalid port number{Style.RESET_ALL}")
                
                elif cmd == "reconnect":
                    if len(command) != 3:
                        print(f"{Fore.RED}Usage: reconnect <host> <port>{Style.RESET_ALL}")
                        continue
                    try:
                        port = int(command[2])
                        success = cli.health_check_peer(command[1], port)
                        if success:
                            peer_id = f"{command[1]}:{port}"
                            with cli.peer_discovery.lock:
                                if peer_id in cli.peer_discovery.peers:
                                    print(f"{Fore.GREEN}Successfully reconnected to {command[1]}:{port}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.YELLOW}Peer {command[1]}:{port} responded but is not in the peer list. Adding...{Style.RESET_ALL}")
                                    cli.peer_discovery._update_peer(command[1], port)
                        else:
                            print(f"{Fore.RED}Failed to reconnect to {command[1]}:{port}{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Invalid port number{Style.RESET_ALL}")
                
                elif cmd == "gossip":
                    # Handle gossip command
                    if len(command) == 1:
                        # Just enable gossip with default settings
                        cli.configure_gossip()
                    elif len(command) == 2:
                        if command[1].lower() == "off":
                            # Disable gossip
                            cli.configure_gossip(enable=False)
                        elif command[1].lower() == "on":
                            # Enable gossip explicitly
                            cli.configure_gossip(enable=True)
                        else:
                            try:
                                # Try to parse as interval
                                interval = float(command[1])
                                cli.configure_gossip(interval=interval)
                            except ValueError:
                                print(f"{Fore.RED}Invalid gossip command. Use 'gossip [on|off|interval]'{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Usage: gossip [on|off|interval]{Style.RESET_ALL}")
                
                elif cmd == "congestion":
                    # Handle congestion control configuration
                    if len(command) < 2:
                        # Just show current configuration
                        cli.configure_aimd()
                    else:
                        kwargs = {}
                        i = 1
                        while i < len(command):
                            if command[i] == "window" and i + 1 < len(command):
                                kwargs["initial_window"] = int(command[i + 1]) * 1024
                                i += 2
                            elif command[i] == "min-window" and i + 1 < len(command):
                                kwargs["min_window"] = int(command[i + 1]) * 1024
                                i += 2
                            elif command[i] == "max-window" and i + 1 < len(command):
                                kwargs["max_window"] = int(command[i + 1]) * 1024
                                i += 2
                            elif command[i] == "timeout":
                                if i + 1 < len(command) and command[i + 1].lower() in ["on", "off"]:
                                    kwargs["timeout_enabled"] = command[i + 1].lower() == "on"
                                    i += 2
                                else:
                                    print(f"{Fore.RED}Invalid timeout setting. Use 'on' or 'off'{Style.RESET_ALL}")
                                    i += 1
                            elif command[i] == "dupack":
                                if i + 1 < len(command) and command[i + 1].lower() in ["on", "off"]:
                                    kwargs["dupack_enabled"] = command[i + 1].lower() == "on"
                                    i += 2
                                else:
                                    print(f"{Fore.RED}Invalid dupack setting. Use 'on' or 'off'{Style.RESET_ALL}")
                                    i += 1
                            elif command[i] == "threshold" and i + 1 < len(command):
                                kwargs["dup_ack_threshold"] = int(command[i + 1])
                                i += 2
                            else:
                                print(f"{Fore.RED}Invalid congestion option: {command[i]}{Style.RESET_ALL}")
                                i += 1
                        
                        cli.configure_aimd(**kwargs)
                
                elif cmd == "send":
                    if len(command) < 4:
                        print(f"{Fore.RED}Usage: send <file> <host> <port> [options]{Style.RESET_ALL}")
                        continue
                    filepath = command[1]
                    target_host = command[2]
                    try:
                        target_port = int(command[3])
                    except ValueError:
                        print(f"{Fore.RED}Invalid port number{Style.RESET_ALL}")
                        continue
                    
                    kwargs = {}
                    i = 4
                    
                    # Check for dual-target mode (two different IPs)
                    if "-dual" in command[i:]:
                        # Switch to multicast mode for dual sending
                        original_mode = cli.current_mode
                        cli.set_mode("multicast")
                        
                        print(f"{Fore.CYAN}Dual-target mode activated.{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}First target: {target_host}:{target_port}{Style.RESET_ALL}")
                        
                        # Get the second target
                        second_target = None
                        while not second_target:
                            target_input = input(f"{Fore.YELLOW}Second target (host:port): {Style.RESET_ALL}").strip()
                            try:
                                host, port = target_input.split(':')
                                port = int(port)
                                second_target = (host, port)
                                print(f"{Fore.GREEN}Second target added: {host}:{port}{Style.RESET_ALL}")
                            except ValueError:
                                print(f"{Fore.RED}Invalid format. Use host:port format.{Style.RESET_ALL}")
                        
                        # Create targets list with both targets
                        targets = [(target_host, target_port), second_target]
                        kwargs["targets"] = targets
                        
                        # Process remaining arguments
                        while i < len(command):
                            if command[i] == "-dual":
                                i += 1  # Skip the dual flag since we've handled it
                            elif command[i] == "-t" and i + 1 < len(command):
                                kwargs["num_threads"] = int(command[i + 1])
                                i += 2
                            elif command[i] == "-b" and i + 1 < len(command):
                                kwargs["bucket_size"] = int(command[i + 1])
                                i += 2
                            elif command[i] == "-r" and i + 1 < len(command):
                                kwargs["token_rate"] = float(command[i + 1])
                                i += 2
                            elif command[i] == "-p" and i + 1 < len(command):
                                kwargs["priority"] = command[i + 1]
                                i += 2
                            elif command[i] == "-g" and i + 1 < len(command):
                                kwargs["group"] = command[i + 1]
                                i += 2
                            elif command[i] == "-m":
                                # Just a flag to enter multicast mode, already handled
                                i += 1
                            elif command[i] == "--port" and i + 1 < len(command):
                                kwargs["port"] = int(command[i + 1])
                                i += 2
                            # AIMD congestion control parameters
                            elif command[i] == "-w" and i + 1 < len(command):
                                # Convert KB to bytes
                                kwargs["initial_window"] = int(command[i + 1]) * 1024
                                i += 2
                            elif command[i] == "-min-w" and i + 1 < len(command):
                                kwargs["min_window"] = int(command[i + 1]) * 1024
                                i += 2
                            elif command[i] == "-max-w" and i + 1 < len(command):
                                kwargs["max_window"] = int(command[i + 1]) * 1024
                                i += 2
                            elif command[i] == "-no-timeout":
                                kwargs["timeout_detection"] = False
                                i += 1
                            elif command[i] == "-no-dupack":
                                kwargs["dupack_detection"] = False
                                i += 1
                            elif command[i] == "-ack-threshold" and i + 1 < len(command):
                                kwargs["dup_ack_threshold"] = int(command[i + 1])
                                i += 2
                            else:
                                print(f"{Fore.RED}Invalid option: {command[i]}{Style.RESET_ALL}")
                                break
                        
                        # Send the file
                        cli.send_file(filepath, target_host, target_port, **kwargs)
                        
                        # Restore original mode if needed
                        if original_mode != "multicast":
                            cli.set_mode(original_mode)
                        continue
                    
                    # Check if we're in multicast mode and need to handle multiple targets
                    if cli.current_mode == "multicast" and "-m" in command[i:]:
                        print(f"{Fore.CYAN}Multicast mode detected. Enter targets (format: host:port).{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Enter an empty line when done.{Style.RESET_ALL}")
                        targets = []
                        targets.append((target_host, target_port))  # Add the first target
                        
                        while True:
                            target_input = input(f"{Fore.YELLOW}Target (host:port): {Style.RESET_ALL}").strip()
                            if not target_input:
                                break
                            try:
                                host, port = target_input.split(':')
                                port = int(port)
                                targets.append((host, port))
                            except ValueError:
                                print(f"{Fore.RED}Invalid format. Use host:port format.{Style.RESET_ALL}")
                        
                        if len(targets) > 1:
                            print(f"{Fore.GREEN}Added {len(targets)} targets for multicast.{Style.RESET_ALL}")
                            kwargs["targets"] = targets
                    
                    while i < len(command):
                        if command[i] == "-t" and i + 1 < len(command):
                            kwargs["num_threads"] = int(command[i + 1])
                            i += 2
                        elif command[i] == "-b" and i + 1 < len(command):
                            kwargs["bucket_size"] = int(command[i + 1])
                            i += 2
                        elif command[i] == "-r" and i + 1 < len(command):
                            kwargs["token_rate"] = float(command[i + 1])
                            i += 2
                        elif command[i] == "-p" and i + 1 < len(command):
                            kwargs["priority"] = command[i + 1]
                            i += 2
                        elif command[i] == "-g" and i + 1 < len(command):
                            kwargs["group"] = command[i + 1]
                            i += 2
                        elif command[i] == "-m":
                            # Just a flag to enter multicast mode, already handled above
                            i += 1
                        elif command[i] == "--port" and i + 1 < len(command):
                            kwargs["port"] = int(command[i + 1])
                            i += 2
                        # AIMD congestion control parameters
                        elif command[i] == "-w" and i + 1 < len(command):
                            # Convert KB to bytes
                            kwargs["initial_window"] = int(command[i + 1]) * 1024
                            i += 2
                        elif command[i] == "-min-w" and i + 1 < len(command):
                            kwargs["min_window"] = int(command[i + 1]) * 1024
                            i += 2
                        elif command[i] == "-max-w" and i + 1 < len(command):
                            kwargs["max_window"] = int(command[i + 1]) * 1024
                            i += 2
                        elif command[i] == "-no-timeout":
                            kwargs["timeout_detection"] = False
                            i += 1
                        elif command[i] == "-no-dupack":
                            kwargs["dupack_detection"] = False
                            i += 1
                        elif command[i] == "-ack-threshold" and i + 1 < len(command):
                            kwargs["dup_ack_threshold"] = int(command[i + 1])
                            i += 2
                        else:
                            print(f"{Fore.RED}Invalid option: {command[i]}{Style.RESET_ALL}")
                            break
                    
                    cli.send_file(filepath, target_host, target_port, **kwargs)
                
                elif cmd == "receive":
                    cli.receive_file()
                
                elif cmd == "multicast-receive" or cmd == "mreceive":
                    # Check if we have a port range specification
                    port_range = 10  # Default
                    if len(command) >= 2:
                        try:
                            port_range = int(command[1])
                            if port_range < 1 or port_range > 100:
                                print(f"{Fore.RED}Port range must be between 1 and 100{Style.RESET_ALL}")
                                port_range = 10
                        except ValueError:
                            print(f"{Fore.RED}Invalid port range, using default (10){Style.RESET_ALL}")
                    
                    cli.start_multicast_receiver(port_range)
                
                elif cmd == "join":
                    if len(command) != 3:
                        print(f"{Fore.RED}Usage: join <host> <port>{Style.RESET_ALL}")
                        continue
                    try:
                        port = int(command[2])
                    except ValueError:
                        print(f"{Fore.RED}Invalid port number{Style.RESET_ALL}")
                        continue
                    cli.join_network(command[1], port)
                
                elif cmd == "quit":
                    cli.stop()
                    break
                
                else:
                    print(f"{Fore.RED}Unknown command: {cmd}{Style.RESET_ALL}")
                    print("Type 'help' for available commands")
                    
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        cli.stop()
        print(f"\n{Fore.YELLOW}Thank you for using our application!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main() 