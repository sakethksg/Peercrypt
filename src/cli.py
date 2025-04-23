import argparse
import sys
import os
import socket
import time
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
    """Check if a port is available."""
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
                    if current_time - peer.last_seen >= self.peer_discovery.gossip_interval * 3:
                        inactive_peers.add((peer.host, peer.port, peer.last_seen))
            
            if inactive_peers:
                print(f"\n{Fore.YELLOW}Inactive peers: {len(inactive_peers)}{Style.RESET_ALL}")
                for i, (host, port, last_seen) in enumerate(inactive_peers):
                    time_ago = int(current_time - last_seen)
                    print(f"  {i+1}. {host}:{port} (last seen {time_ago} seconds ago)")
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
            else:
                print("Transfer failed")
                self.failed_transfers += 1
            
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
        """Show current status and detailed command documentation"""
        print("\nCurrent Status:")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Mode: {self.current_mode}")
        
        if self.current_mode == "token-bucket":
            print("\nToken Bucket Status:")
            print(f"Bucket Size: {self.transfer_modes[self.current_mode].bucket.capacity} tokens")
            print(f"Token Rate: {self.transfer_modes[self.current_mode].bucket.rate} tokens/sec")
            print(f"Current Tokens: {self.transfer_modes[self.current_mode].bucket.get_available_tokens()}")
            print(f"Adaptive Rate: {self.transfer_modes[self.current_mode].bucket.adaptive_rate:.2f} tokens/sec")

        elif self.current_mode == "normal":
            print("\nNormal Mode Status:")
            print("No specific status information available for normal mode")
        
        elif self.current_mode == "parallel":
            print("\nParallel Mode Status:")
            print(f"Default Threads: {self.transfer_modes[self.current_mode].default_num_threads}")
            print(f"Chunk Size: {self.transfer_modes[self.current_mode].chunk_size} bytes")
        
        elif self.current_mode == "qos":
            print("\nQoS Status:")
            print("Priority levels: high, normal, low")
        
        elif self.current_mode == "aimd":
            print("\nAIMD Status:")
            print("Using adaptive congestion control")
            print("Bandwidth statistics will be saved to CSV")
            
            # Add detailed AIMD parameters
            aimd_config = self.transfer_modes["aimd"].configure()
            print(f"Window size: {aimd_config['initial_window']//1024} KB")
            print(f"Min window: {aimd_config['min_window']//1024} KB")
            print(f"Max window: {aimd_config['max_window']//1024} KB")
            print(f"Timeout detection: {'Enabled' if aimd_config['timeout_enabled'] else 'Disabled'}")
            print(f"Triple DupACK detection: {'Enabled' if aimd_config['dupack_enabled'] else 'Disabled'}")
            print(f"DupACK threshold: {aimd_config['dup_ack_threshold']}")
            
            print("\nPerformance Notes:")
            print("- Larger window sizes can increase throughput but may cause more congestion")
            print("- Timeout detection is more conservative but works in all network conditions")
            print("- Triple duplicate ACK detection enables faster recovery from packet loss")
            print("- Disabling both detection mechanisms will prevent congestion control")
            print("- For reliable networks, you can set a larger window size and disable timeout detection")
            print("- For lossy networks, enable both detection mechanisms with a smaller window")
            
            print("\nConfigure with: 'congestion' command or when sending files with options:")
            print("  -w <size>            - Set window size in KB")
            print("  -no-timeout          - Disable timeout detection")
            print("  -no-dupack           - Disable duplicate ACK detection")
            print("  -ack-threshold <num> - Set threshold for duplicate ACKs")
        
        elif self.current_mode == "multicast":
            print("\nMulticast Mode Status:")
            print("Can send to multiple targets simultaneously")
            print(f"Base Port: {self.port}")
            print("Use the multicast-receive command to start a multicast receiver")
        
        print("\nAvailable Commands:")
        print("\n1. Network Management:")
        print("  list-peers - List all active peers in the network")
        print("  join <host> <port> - Join network via bootstrap peer")
        print("    Example: join 192.168.1.100 5000")
        print("  gossip [on|off|interval] - Configure gossip-based peer discovery")
        print("    Example: gossip 10.0 (sets interval to 10 seconds)")
        print("    Example: gossip off (disables gossip)")
        
        print("\n2. Transfer Mode Configuration:")
        print("  set-mode <mode> - Change transfer mode")
        print("    Available modes: normal, token-bucket, aimd, qos, parallel, multicast")
        print("    Example: set-mode token-bucket")
        
        print("\n3. File Transfer:")
        print("  send <file> <host> <port> [options] - Send a file")
        print("    Example: send document.pdf 192.168.1.100 5000")
        print("  send <file> <host> <port> -dual - Send to two devices with different IPs")
        print("    Example: send document.pdf 192.168.1.100 5000 -dual")
        print("  receive - Start receiving files")
        if "multicast" in self.transfer_modes:
            print("  multicast-receive [port_range] - Start multicast receiver on multiple ports")
            print("    Example: multicast-receive 5")
            print("  mreceive - Shorthand for multicast-receive")
        
        print("\n4. Mode-Specific Options:")
        if self.current_mode == "token-bucket":
            print("\nToken Bucket Options:")
            print("  -b <size> - Set bucket size in tokens (default: 1024)")
            print("  -r <rate> - Set token rate in tokens/sec (default: 100)")
            print("    Example: send file.txt 192.168.1.100 5000 -b 2048 -r 200")
        
        elif self.current_mode == "parallel":
            print("\nParallel Mode Options:")
            print("  -t <threads> - Set number of parallel threads (default: 2)")
            print("    Example: send largefile.iso 192.168.1.100 5000 -t 4")
        
        elif self.current_mode == "qos":
            print("\nQoS Options:")
            print("  -p <priority> - Set transfer priority (high/normal/low)")
            print("    Example: send important.pdf 192.168.1.100 5000 -p high")
        
        elif self.current_mode == "aimd":
            print("\nAIMD Congestion Control Options:")
            print("  -w <size> - Set initial window size in KB (default: 1)")
            print("    • Low (1-4): Good for unstable networks with high packet loss")
            print("    • Medium (8-16): Balanced performance for most networks")
            print("    • High (32-64): Best for reliable, high-bandwidth networks")
            
            print("  -min-w <size> - Set minimum window size in KB (default: 1)")
            print("    • Higher values prevent throughput from dropping too low during congestion")
            
            print("  -max-w <size> - Set maximum window size in KB (default: 64)")
            print("    • Limits bandwidth consumption; useful for shared networks")
            
            print("  -no-timeout - Disable timeout-based congestion detection")
            print("    • Can improve performance on reliable networks with occasional packet reordering")
            
            print("  -no-dupack - Disable duplicate ACK-based congestion detection")
            print("    • Can help when network frequently reorders packets but doesn't drop them")
            
            print("  -ack-threshold <count> - Set duplicate ACK threshold (default: 3)")
            print("    • Higher values (4-5): Less sensitive to reordering, fewer false positives")
            print("    • Lower values (2): Faster response to actual packet loss")
            
            print("\n  Examples for specific scenarios:")
            print("    • Large file over reliable network:")
            print("      send large-file.dat 192.168.1.100 5000 -w 32 -min-w 8")
            print("    • Small file over lossy WiFi:")
            print("      send small-file.txt 192.168.1.100 5000 -w 4 -max-w 16")
            print("    • Medium file over network with packet reordering:")
            print("      send medium-file.pdf 192.168.1.100 5000 -no-timeout -ack-threshold 5")
        
        elif self.current_mode == "multicast":
            print("\nMulticast Mode Options:")
            print("  -m - Interactive mode to add multiple targets")
            print("    Example: send file.txt 192.168.1.100 5000 -m")
            print("  -dual - Send to exactly two targets with different IPs")
            print("    Example: send file.txt 192.168.1.100 5000 -dual")
            print("  When using multicast mode, you can send to multiple receivers simultaneously")
            print("  The first target is specified on the command line, then you can add more interactively")
        
        print("\n5. System Commands:")
        print("  status - Show current status and this help message")
        print("  gossip [on|off|interval] - Configure gossip-based peer discovery")
        print("    Example: gossip 10.0 (sets interval to 10 seconds)")
        print("  congestion - Configure AIMD congestion control parameters")
        print("    Example: congestion window 8 timeout off (sets window size to 8KB, disables timeout detection)")
        print("    Example: congestion dupack on threshold 3 (enables triple duplicate ACK detection)")
        print("  help - Show this help message")
        print("  quit - Exit the application")
        
        print("\nAdditional Information:")
        print("- All file transfers are encrypted using AES-256")
        print("- Transfer statistics are saved to JSON files")
        print("- AIMD congestion control uses both timeout and triple duplicate ACK detection")
        print("- Use Ctrl+C to cancel ongoing transfers")
        print("- Type 'help' anytime to see this message")

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