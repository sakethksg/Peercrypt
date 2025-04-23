import socket
import threading
import time
import json
from typing import Set, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Peer:
    host: str
    port: int
    last_seen: float
    status: str  # 'active', 'inactive', 'unknown'

class PeerDiscovery:
    def __init__(self, host: str, port: int, gossip_interval: float = 5.0):
        self.host = host
        self.port = port
        self.gossip_interval = gossip_interval
        self.peers: Dict[str, Peer] = {}
        self.lock = threading.Lock()
        self.running = False
        self.gossip_socket = None
        self.discovery_socket = None

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

    def stop(self):
        """Stop the peer discovery service."""
        self.running = False
        if self.gossip_socket:
            self.gossip_socket.close()
        if self.discovery_socket:
            self.discovery_socket.close()

    def _gossip_loop(self):
        """Main gossip loop that periodically sends peer information to other peers."""
        self.gossip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while self.running:
            try:
                # Get current peer list
                with self.lock:
                    peer_list = list(self.peers.values())
                
                # Send to a random subset of peers
                for peer in peer_list[:3]:  # Send to up to 3 random peers
                    try:
                        message = {
                            'type': 'gossip',
                            'peers': [asdict(p) for p in peer_list],
                            'source': {'host': self.host, 'port': self.port}
                        }
                        self.gossip_socket.sendto(
                            json.dumps(message).encode(),
                            (peer.host, peer.port)
                        )
                    except Exception as e:
                        print(f"Error sending gossip to {peer.host}:{peer.port}: {e}")
                
                time.sleep(self.gossip_interval)
            except Exception as e:
                print(f"Error in gossip loop: {e}")
                time.sleep(1)

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
            except Exception as e:
                print(f"Error in discovery listener: {e}")

    def _handle_gossip(self, message: dict, addr: tuple):
        """Handle incoming gossip messages."""
        try:
            source = message['source']
            peers = message['peers']
            
            with self.lock:
                # Update source peer
                self._update_peer(source['host'], source['port'])
                
                # Update other peers
                for peer_data in peers:
                    self._update_peer(peer_data['host'], peer_data['port'])
        except Exception as e:
            print(f"Error handling gossip: {e}")

    def _handle_join(self, message: dict, addr: tuple):
        """Handle join requests from new peers."""
        try:
            host, port = addr
            with self.lock:
                self._update_peer(host, port)
                
                # Send acknowledgment
                response = {
                    'type': 'join_ack',
                    'peers': [asdict(p) for p in self.peers.values()]
                }
                self.discovery_socket.sendto(
                    json.dumps(response).encode(),
                    addr
                )
        except Exception as e:
            print(f"Error handling join: {e}")

    def _update_peer(self, host: str, port: int):
        """Update or add a peer to the peer list."""
        peer_id = f"{host}:{port}"
        current_time = time.time()
        
        if peer_id in self.peers:
            self.peers[peer_id].last_seen = current_time
            self.peers[peer_id].status = 'active'
        else:
            self.peers[peer_id] = Peer(
                host=host,
                port=port,
                last_seen=current_time,
                status='active'
            )

    def get_active_peers(self) -> Set[tuple]:
        """Get the set of currently active peers."""
        with self.lock:
            current_time = time.time()
            active_peers = set()
            
            for peer in self.peers.values():
                if current_time - peer.last_seen < self.gossip_interval * 3:
                    active_peers.add((peer.host, peer.port))
                else:
                    peer.status = 'inactive'
            
            return active_peers

    def join_network(self, bootstrap_host: str, bootstrap_port: int) -> bool:
        """Join the network using a bootstrap peer."""
        try:
            message = {
                'type': 'join',
                'peer': {'host': self.host, 'port': self.port}
            }
            
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(
                    json.dumps(message).encode(),
                    (bootstrap_host, bootstrap_port)
                )
                
                # Wait for acknowledgment
                s.settimeout(5.0)
                data, _ = s.recvfrom(65535)
                response = json.loads(data.decode())
                
                if response['type'] == 'join_ack':
                    with self.lock:
                        for peer_data in response['peers']:
                            self._update_peer(peer_data['host'], peer_data['port'])
                    return True
            return False
        except Exception as e:
            print(f"Error joining network: {e}")
            return False 