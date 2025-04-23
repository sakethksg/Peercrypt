import time
import socket
import os
import threading
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from tqdm import tqdm
from utils.encryption import encrypt_data, decrypt_data

@dataclass
class TransferPriority:
    level: int
    min_bandwidth: int  # in bytes per second
    weight: float

class QoSManager:
    def __init__(self):
        self.transfers: Dict[str, TransferPriority] = {}
        self.lock = threading.Lock()
        self.total_bandwidth = 1000000  # 1 MB/s default
        self.available_bandwidth = self.total_bandwidth

    def add_transfer(self, transfer_id: str, priority: TransferPriority):
        with self.lock:
            self.transfers[transfer_id] = priority
            self._recalculate_bandwidth()

    def remove_transfer(self, transfer_id: str):
        with self.lock:
            if transfer_id in self.transfers:
                del self.transfers[transfer_id]
                self._recalculate_bandwidth()

    def _recalculate_bandwidth(self):
        total_weight = sum(t.weight for t in self.transfers.values())
        if total_weight == 0:
            return

        for transfer_id, priority in self.transfers.items():
            allocated_bandwidth = int((priority.weight / total_weight) * self.total_bandwidth)
            priority.min_bandwidth = max(priority.min_bandwidth, allocated_bandwidth)

    def get_transfer_bandwidth(self, transfer_id: str) -> int:
        with self.lock:
            if transfer_id in self.transfers:
                return self.transfers[transfer_id].min_bandwidth
            return 0

class QoSMode:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.chunk_size = 8192
        self.qos_manager = QoSManager()
        self.transfer_speeds: Dict[str, float] = {}
        self.lock = threading.Lock()

    def _calculate_chunk_delay(self, transfer_id: str, chunk_size: int) -> float:
        bandwidth = self.qos_manager.get_transfer_bandwidth(transfer_id)
        if bandwidth == 0:
            return 0
        return (chunk_size / bandwidth) * 1000  # Convert to milliseconds

    def send_file(self, filepath: str, target_host: str, target_port: int, 
                 priority_level: int = 1, min_bandwidth: int = 100000, **kwargs) -> bool:
        try:
            transfer_id = f"{filepath}_{time.time()}"
            priority = TransferPriority(
                level=priority_level,
                min_bandwidth=min_bandwidth,
                weight=1.0 / priority_level  # Higher priority = higher weight
            )
            self.qos_manager.add_transfer(transfer_id, priority)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_host, target_port))
                
                # Send filename
                filename = os.path.basename(filepath)
                s.send(filename.encode())
                s.recv(1024)  # Wait for acknowledgment
                
                # Send file size
                file_size = os.path.getsize(filepath)
                s.send(str(file_size).encode())
                s.recv(1024)  # Wait for acknowledgment
                
                bytes_sent = 0
                start_time = time.time()
                
                with open(filepath, 'rb') as f:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Sending {filename}") as pbar:
                        while bytes_sent < file_size:
                            # Read data from file
                            data = f.read(self.chunk_size)
                            if not data:
                                break
                                
                            # Encrypt the data
                            encrypted_data = encrypt_data(data)
                            
                            # Send length of encrypted data first
                            s.send(len(encrypted_data).to_bytes(4, 'big'))
                            # Then send the encrypted data
                            s.send(encrypted_data)
                            
                            bytes_sent += len(data)
                            pbar.update(len(data))
                            
                            # Rate limiting based on QoS
                            delay = self._calculate_chunk_delay(transfer_id, len(data))
                            if delay > 0:
                                time.sleep(delay / 1000)  # Convert to seconds
                            
                            # Update transfer speed
                            elapsed_time = time.time() - start_time
                            with self.lock:
                                self.transfer_speeds[transfer_id] = bytes_sent / elapsed_time
                
                transfer_time = time.time() - start_time
                speed = file_size / transfer_time / 1024 if transfer_time > 0 else 0
                print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                
                self.qos_manager.remove_transfer(transfer_id)
                return True
        except Exception as e:
            print(f"Error sending file: {e}")
            if 'transfer_id' in locals():
                self.qos_manager.remove_transfer(transfer_id)
            return False

    def receive_file(self) -> Tuple[bool, Optional[str]]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen(1)
                
                conn, addr = s.accept()
                with conn:
                    # Receive filename
                    filename = conn.recv(1024).decode()
                    conn.send(b"OK")
                    
                    # Receive file size
                    file_size = int(conn.recv(1024).decode())
                    conn.send(b"OK")
                    
                    transfer_id = f"receive_{filename}_{time.time()}"
                    priority = TransferPriority(
                        level=1,
                        min_bandwidth=100000,
                        weight=1.0
                    )
                    self.qos_manager.add_transfer(transfer_id, priority)
                    
                    bytes_received = 0
                    start_time = time.time()
                    
                    with open(f"received_{filename}", 'wb') as f:
                        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Receiving {filename}") as pbar:
                            while bytes_received < file_size:
                                # First receive the length of the encrypted data
                                length_bytes = conn.recv(4)
                                if not length_bytes:
                                    break
                                
                                length = int.from_bytes(length_bytes, 'big')
                                
                                # Then receive the encrypted data
                                encrypted_data = b''
                                while len(encrypted_data) < length:
                                    chunk = conn.recv(min(length - len(encrypted_data), self.chunk_size))
                                    if not chunk:
                                        break
                                    encrypted_data += chunk
                                
                                if not encrypted_data:
                                    break
                                
                                # Decrypt the data and write to file
                                data = decrypt_data(encrypted_data)
                                if data:
                                    f.write(data)
                                    bytes_received += len(data)
                                    pbar.update(len(data))
                                
                                # Update transfer speed
                                elapsed_time = time.time() - start_time
                                with self.lock:
                                    self.transfer_speeds[transfer_id] = bytes_received / elapsed_time
                    
                    transfer_time = time.time() - start_time
                    speed = file_size / transfer_time / 1024 if transfer_time > 0 else 0
                    print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                    
                    self.qos_manager.remove_transfer(transfer_id)
                    return True, f"received_{filename}"
        except Exception as e:
            print(f"Error receiving file: {e}")
            if 'transfer_id' in locals():
                self.qos_manager.remove_transfer(transfer_id)
            return False, None

    def get_transfer_speeds(self) -> Dict[str, float]:
        with self.lock:
            return self.transfer_speeds.copy() 