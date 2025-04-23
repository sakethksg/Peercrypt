import socket
import threading
import time
import json
import random
import logging
from typing import Set, Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class Peer:
    host: str
    port: int
    last_seen: float
    status: str  # 'active', 'inactive', 'unknown'
    failed_attempts: int = 0
    rtt: float = 0.0  # Round-trip time (latency measurement)
    reliability: float = 1.0  # Reliability score (1.0 = perfect)

class PeerDiscovery:
    def __init__(self, host: str, port: int, gossip_interval: float = 5.0, 
                max_retries: int = 3, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.gossip_interval = gossip_interval
        self.max_retries = max_retries
        self.timeout = timeout
        self.peers: Dict[str, Peer] = {}
        self.lock = threading.Lock()
        self.running = False
        self.gossip_socket = None
        self.discovery_socket = None
        self.health_check_thread = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("PeerDiscovery")

    def start(self):
        """Start the peer discovery service."""
        self.running = True
        
        # Start gossip thread
        self.gossip_thread = threading.Thread(target=self._gossip_loop)
        self.gossip_thread.daemon = True
        self.gossip_thread.start()
        
        # Start discovery listener
        self.discovery_thread = threading.Thread(target=self._discovery_listener)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        
        # Start health check thread
        self.health_check_thread = threading.Thread(target=self._health_check_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        
        self.logger.info(f"Peer discovery started on {self.host}:{self.port}")

    def stop(self):
        """Stop the peer discovery service."""
        self.running = False
        if self.gossip_socket:
            self.gossip_socket.close()
        if self.discovery_socket:
            self.discovery_socket.close()
        self.logger.info("Peer discovery stopped")

    def _gossip_loop(self):
        """Main gossip loop that periodically sends peer information to other peers."""
        self.gossip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while self.running:
            try:
                # Get current peer list
                with self.lock:
                    peer_list = list(self.peers.values())
                
                # Filter to active peers only
                active_peers = [p for p in peer_list if p.status == 'active']
                
                if not active_peers:
                    time.sleep(self.gossip_interval)
                    continue
                
                # Send to a random subset of peers, prioritizing more reliable peers
                selected_peers = self._select_gossip_targets(active_peers)
                
                for peer in selected_peers:
                    try:
                        message = {
                            'type': 'gossip',
                            'peers': [asdict(p) for p in peer_list if p.status == 'active'],
                            'source': {'host': self.host, 'port': self.port},
                            'timestamp': time.time()
                        }
                        
                        # Attempt to send with retries
                        self._send_with_retry(
                            self.gossip_socket, 
                            message, 
                            (peer.host, peer.port)
                        )
                    except Exception as e:
                        self.logger.warning(f"Error sending gossip to {peer.host}:{peer.port}: {e}")
                        self._mark_peer_failure(peer.host, peer.port)
                
                time.sleep(self.gossip_interval)
            except Exception as e:
                self.logger.error(f"Error in gossip loop: {e}")
                time.sleep(1)
    
    def _select_gossip_targets(self, peers: List[Peer], count: int = 3) -> List[Peer]:
        """Select peers for gossip, prioritizing more reliable ones."""
        if not peers:
            return []
            
        # Sort by reliability score
        sorted_peers = sorted(peers, key=lambda p: p.reliability, reverse=True)
        
        # Always include the most reliable peer(s)
        selected = sorted_peers[:min(2, len(sorted_peers))]
        
        # Randomly select additional peers, weighted by reliability
        remaining = sorted_peers[min(2, len(sorted_peers)):]
        if remaining and len(selected) < count:
            weights = [p.reliability for p in remaining]
            # Normalize weights
            sum_weights = sum(weights) or 1.0  # Avoid division by zero
            weights = [w/sum_weights for w in weights]
            
            # Select remaining peers with weighted probability
            additional = random.choices(
                remaining, 
                weights=weights, 
                k=min(count-len(selected), len(remaining))
            )
            selected.extend(additional)
        
        return selected

    def _send_with_retry(self, sock: socket.socket, message: dict, addr: tuple) -> bool:
        """Send a message with retry logic."""
        retries = 0
        start_time = time.time()
        
        while retries < self.max_retries:
            try:
                sock.sendto(json.dumps(message).encode(), addr)
                
                # If this is not a message that expects a response, return immediately
                if message.get('type') not in ['join', 'health_check']:
                    if retries > 0:
                        self.logger.info(f"Successfully sent to {addr[0]}:{addr[1]} after {retries} retries")
                    return True
                    
                # For messages expecting response, wait for it
                sock.settimeout(self.timeout)
                data, resp_addr = sock.recvfrom(65535)
                
                # Calculate RTT and update peer metrics
                rtt = time.time() - start_time
                with self.lock:
                    peer_id = f"{addr[0]}:{addr[1]}"
                    if peer_id in self.peers:
                        self.peers[peer_id].rtt = rtt
                        self.peers[peer_id].reliability = min(1.0, self.peers[peer_id].reliability + 0.1)
                
                return True
            except socket.timeout:
                retries += 1
                self.logger.warning(f"Timeout sending to {addr[0]}:{addr[1]}, retry {retries}/{self.max_retries}")
                # Increase timeout for next retry
                self.timeout = min(10.0, self.timeout * 1.5)
            except Exception as e:
                self.logger.error(f"Error sending to {addr[0]}:{addr[1]}: {e}")
                retries += 1
        
        # Mark peer as potentially problematic
        self._mark_peer_failure(addr[0], addr[1])
        return False

    def _mark_peer_failure(self, host: str, port: int):
        """Mark a peer as having a connection failure."""
        with self.lock:
            peer_id = f"{host}:{port}"
            if peer_id in self.peers:
                self.peers[peer_id].failed_attempts += 1
                self.peers[peer_id].reliability = max(0.1, self.peers[peer_id].reliability - 0.2)
                
                # If too many failures, mark as inactive
                if self.peers[peer_id].failed_attempts >= self.max_retries:
                    self.peers[peer_id].status = 'inactive'
                    self.logger.warning(f"Peer {host}:{port} marked as inactive after {self.peers[peer_id].failed_attempts} failures")

    def _discovery_listener(self):
        """Listen for incoming peer discovery messages."""
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.bind((self.host, self.port))
        
        while self.running:
            try:
                data, addr = self.discovery_socket.recvfrom(65535)
                message = json.loads(data.decode())
                
                if message['type'] == 'gossip':
                    self._handle_gossip(message, addr)
                elif message['type'] == 'join':
                    self._handle_join(message, addr)
                elif message['type'] == 'health_check':
                    self._handle_health_check(message, addr)
            except json.JSONDecodeError:
                self.logger.warning(f"Received invalid JSON from {addr[0]}:{addr[1]}")
            except Exception as e:
                self.logger.error(f"Error in discovery listener: {e}")

    def _handle_gossip(self, message: dict, addr: tuple):
        """Handle incoming gossip messages."""
        try:
            source = message['source']
            peers = message['peers']
            timestamp = message.get('timestamp', time.time())
            
            # Check message age
            if time.time() - timestamp > self.gossip_interval * 3:
                self.logger.warning(f"Discarding outdated gossip message from {addr[0]}:{addr[1]}")
                return
            
            with self.lock:
                # Update source peer
                self._update_peer(source['host'], source['port'])
                
                # Update other peers
                for peer_data in peers:
                    self._update_peer(peer_data['host'], peer_data['port'])
        except Exception as e:
            self.logger.error(f"Error handling gossip: {e}")

    def _handle_join(self, message: dict, addr: tuple):
        """Handle join requests from new peers."""
        try:
            host, port = addr
            
            with self.lock:
                self._update_peer(host, port)
                
                # Send acknowledgment with only active peers
                active_peers = [p for p in self.peers.values() if p.status == 'active']
                response = {
                    'type': 'join_ack',
                    'peers': [asdict(p) for p in active_peers]
                }
                self.discovery_socket.sendto(
                    json.dumps(response).encode(),
                    addr
                )
                self.logger.info(f"New peer joined: {host}:{port}")
        except Exception as e:
            self.logger.error(f"Error handling join: {e}")

    def _handle_health_check(self, message: dict, addr: tuple):
        """Handle health check requests."""
        try:
            response = {
                'type': 'health_check_ack',
                'status': 'healthy',
                'timestamp': time.time()
            }
            self.discovery_socket.sendto(
                json.dumps(response).encode(),
                addr
            )
            
            # Update the peer that sent the health check
            with self.lock:
                self._update_peer(addr[0], addr[1])
        except Exception as e:
            self.logger.error(f"Error handling health check: {e}")

    def _update_peer(self, host: str, port: int):
        """Update or add a peer to the peer list."""
        peer_id = f"{host}:{port}"
        current_time = time.time()
        
        # Don't add ourselves
        if host == self.host and port == self.port:
            return
            
        if peer_id in self.peers:
            self.peers[peer_id].last_seen = current_time
            self.peers[peer_id].status = 'active'
            # Reset failed attempts on successful contact
            if self.peers[peer_id].failed_attempts > 0:
                self.peers[peer_id].failed_attempts = 0
        else:
            self.peers[peer_id] = Peer(
                host=host,
                port=port,
                last_seen=current_time,
                status='active'
            )
            self.logger.info(f"New peer discovered: {host}:{port}")

    def _health_check_loop(self):
        """Periodically check health of inactive peers to re-enable them."""
        health_check_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        health_check_sock.settimeout(self.timeout)
        
        while self.running:
            try:
                time.sleep(self.gossip_interval * 2)  # Check less frequently than gossip
                
                with self.lock:
                    peers_to_check = []
                    for peer_id, peer in self.peers.items():
                        # Check inactive or potentially problematic peers
                        if (peer.status == 'inactive' or peer.failed_attempts > 0) and \
                           time.time() - peer.last_seen > self.gossip_interval * 3:
                            peers_to_check.append(peer)
                
                # Perform health checks
                for peer in peers_to_check:
                    try:
                        message = {
                            'type': 'health_check',
                            'source': {'host': self.host, 'port': self.port},
                            'timestamp': time.time()
                        }
                        
                        success = self._send_with_retry(
                            health_check_sock, 
                            message, 
                            (peer.host, peer.port)
                        )
                        
                        if success:
                            with self.lock:
                                peer_id = f"{peer.host}:{peer.port}"
                                if peer_id in self.peers:
                                    self.peers[peer_id].status = 'active'
                                    self.peers[peer_id].failed_attempts = 0
                                    self.logger.info(f"Peer {peer.host}:{peer.port} recovered through health check")
                    except Exception as e:
                        self.logger.warning(f"Health check failed for {peer.host}:{peer.port}: {e}")
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                
    def get_active_peers(self) -> Set[tuple]:
        """Get the set of currently active peers."""
        with self.lock:
            active_peers = set()
            
            for peer in self.peers.values():
                if peer.status == 'active':
                    active_peers.add((peer.host, peer.port))
            
            return active_peers
    
    def get_reliable_peers(self, min_reliability: float = 0.5) -> List[Tuple[str, int, float]]:
        """Get list of peers above a reliability threshold, sorted by reliability."""
        with self.lock:
            reliable_peers = []
            
            for peer in self.peers.values():
                if peer.status == 'active' and peer.reliability >= min_reliability:
                    reliable_peers.append((peer.host, peer.port, peer.reliability))
            
            # Sort by reliability (highest first)
            return sorted(reliable_peers, key=lambda p: p[2], reverse=True)

    def join_network(self, bootstrap_host: str, bootstrap_port: int) -> bool:
        """Join the network using a bootstrap peer with retry mechanism."""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Joining network via {bootstrap_host}:{bootstrap_port}, attempt {attempt+1}/{self.max_retries}")
                message = {
                    'type': 'join',
                    'peer': {'host': self.host, 'port': self.port},
                    'timestamp': time.time()
                }
                
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(self.timeout * (attempt + 1))  # Increase timeout with each retry
                    s.sendto(
                        json.dumps(message).encode(),
                        (bootstrap_host, bootstrap_port)
                    )
                    
                    # Wait for acknowledgment
                    data, _ = s.recvfrom(65535)
                    response = json.loads(data.decode())
                    
                    if response['type'] == 'join_ack':
                        with self.lock:
                            for peer_data in response['peers']:
                                self._update_peer(peer_data['host'], peer_data['port'])
                        self.logger.info(f"Successfully joined network with {len(response['peers'])} peers")
                        return True
            except socket.timeout:
                self.logger.warning(f"Timeout joining network, attempt {attempt+1}/{self.max_retries}")
            except Exception as e:
                self.logger.error(f"Error joining network: {e}")
                
        self.logger.error(f"Failed to join network after {self.max_retries} attempts")
        return False 