import time
import socket
import os
import threading
import queue
from typing import List, Tuple, Dict, Optional, Set
from tqdm import tqdm
from utils.encryption import encrypt_data, decrypt_data

class MulticastMode:
    """
    Transfer mode that enables sending files to multiple devices simultaneously.
    Uses separate threads to handle each receiver connection.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.base_port = port  # Base port for multicast operation
        self.chunk_size = 8192
        self.receiver_threads = []
        self.active_receivers = set()  # Set of active receiver addresses
        self.status_lock = threading.Lock()
        self.transfer_complete = threading.Event()
        self.results = {}  # Store results from each receiver
        self.error_queue = queue.Queue()  # Queue for error messages
        
    def send_file(self, filepath: str, targets: List[Tuple[str, int]], **kwargs) -> bool:
        """
        Send a file to multiple targets simultaneously
        
        Args:
            filepath: Path to the file to send
            targets: List of (host, port) tuples representing target devices
            **kwargs: Additional parameters
                - timeout: Connection timeout in seconds (default: 30)
        
        Returns:
            True if the file was sent to all targets successfully, False otherwise
        """
        if not targets:
            print("Error: No targets specified")
            return False
        
        timeout = kwargs.get('timeout', 30)
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        
        print(f"Starting multicast transfer of {filename} ({file_size / 1024:.2f} KB) to {len(targets)} receivers")
        
        # Read file data once
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Encrypt the data once
        try:
            encrypted_data = encrypt_data(file_data)
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return False
            
        # Clear previous state
        self.transfer_complete.clear()
        self.receiver_threads = []
        self.active_receivers = set()
        self.results = {}
        
        # Start a thread for each target
        for i, (target_host, target_port) in enumerate(targets):
            thread = threading.Thread(
                target=self._send_to_single_target,
                args=(target_host, target_port, filename, file_size, encrypted_data, i),
                daemon=True
            )
            self.receiver_threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete or timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            if all(not t.is_alive() for t in self.receiver_threads):
                break
            time.sleep(0.1)
            
            # Check for errors
            if not self.error_queue.empty():
                error = self.error_queue.get()
                print(f"Error encountered: {error}")
            
        # Check results
        all_success = True
        for i, (target_host, target_port) in enumerate(targets):
            result = self.results.get(i, False)
            if result:
                print(f"✓ Successfully sent to {target_host}:{target_port}")
            else:
                print(f"✗ Failed to send to {target_host}:{target_port}")
                all_success = False
        
        return all_success
    
    def _send_to_single_target(self, target_host: str, target_port: int, 
                              filename: str, file_size: int, encrypted_data: bytes, 
                              thread_id: int):
        """
        Send file to a single target (runs in a separate thread)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Connection timeout
                s.connect((target_host, target_port))
                
                # Register active receiver
                with self.status_lock:
                    self.active_receivers.add((target_host, target_port))
                
                # Send filename
                s.send(filename.encode())
                s.recv(1024)  # Wait for acknowledgment
                
                # Send file size
                s.send(str(file_size).encode())
                s.recv(1024)  # Wait for acknowledgment
                
                # Send data in chunks
                bytes_sent = 0
                with tqdm(total=file_size, unit='B', unit_scale=True, 
                          desc=f"Sending to {target_host}:{target_port}") as pbar:
                    
                    # Send length of encrypted data first
                    s.send(len(encrypted_data).to_bytes(4, 'big'))
                    
                    # Then send the encrypted data
                    s.send(encrypted_data)
                    
                    bytes_sent = file_size
                    pbar.update(file_size)
                
                # Wait for final acknowledgment
                s.settimeout(10)  # Longer timeout for final ack
                ack = s.recv(1024)
                if ack == b"COMPLETE":
                    self.results[thread_id] = True
                    return True
                else:
                    self.results[thread_id] = False
                    return False
                
        except Exception as e:
            self.error_queue.put(f"Error sending to {target_host}:{target_port}: {e}")
            self.results[thread_id] = False
            return False
        finally:
            # Unregister receiver
            with self.status_lock:
                self.active_receivers.discard((target_host, target_port))
    
    def receive_file(self) -> Tuple[bool, Optional[str]]:
        """
        Receive a file from a sender
        
        Returns:
            Tuple of (success_flag, received_filename)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(1)
                
                print(f"Waiting for connection on {self.host}:{self.port}...")
                conn, addr = s.accept()
                print(f"Connected to {addr[0]}:{addr[1]}")
                
                with conn:
                    # Receive filename
                    filename = conn.recv(1024).decode()
                    conn.send(b"OK")
                    
                    # Receive file size
                    file_size = int(conn.recv(1024).decode())
                    conn.send(b"OK")
                    
                    # Receive data
                    bytes_received = 0
                    with open(f"received_{filename}", 'wb') as f:
                        with tqdm(total=file_size, unit='B', unit_scale=True, 
                                 desc=f"Receiving {filename}") as pbar:
                            
                            # First receive the length of the encrypted data
                            length_bytes = conn.recv(4)
                            if not length_bytes:
                                return False, None
                                
                            length = int.from_bytes(length_bytes, 'big')
                            
                            # Then receive the encrypted data
                            encrypted_data = b''
                            while len(encrypted_data) < length:
                                chunk = conn.recv(min(length - len(encrypted_data), self.chunk_size))
                                if not chunk:
                                    break
                                encrypted_data += chunk
                                
                                # Update progress based on received encrypted data
                                pbar.update(len(chunk))
                            
                            # Decrypt the data
                            data = decrypt_data(encrypted_data)
                            if data:
                                f.write(data)
                                bytes_received = len(data)
                    
                    # Send completion acknowledgment
                    conn.send(b"COMPLETE")
                    
                    print(f"\nReceived {bytes_received / 1024:.2f} KB successfully")
                    return True, f"received_{filename}"
                    
        except Exception as e:
            print(f"Error receiving file: {e}")
            return False, None
    
    def start_multicast_receiver(self, port_range: int = 10) -> None:
        """
        Start multiple receiver threads to listen on a range of ports
        
        Args:
            port_range: Number of consecutive ports to listen on
        """
        receivers = []
        for port_offset in range(port_range):
            receiver_port = self.base_port + port_offset
            receiver_thread = threading.Thread(
                target=self._receiver_thread,
                args=(receiver_port,),
                daemon=True
            )
            receivers.append(receiver_thread)
            receiver_thread.start()
            print(f"Started receiver on port {receiver_port}")
        
        print(f"Multicast receiver started on ports {self.base_port}-{self.base_port + port_range - 1}")
        print("Press Ctrl+C to stop receiving")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping multicast receiver")
    
    def _receiver_thread(self, port: int) -> None:
        """
        Thread function for a single receiver port
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, port))
                s.listen(1)
                
                while True:
                    try:
                        conn, addr = s.accept()
                        with conn:
                            # Receive filename
                            filename = conn.recv(1024).decode()
                            conn.send(b"OK")
                            
                            # Receive file size
                            file_size = int(conn.recv(1024).decode())
                            conn.send(b"OK")
                            
                            # Unique filename to avoid collisions
                            unique_filename = f"received_{addr[0]}_{addr[1]}_{filename}"
                            
                            # Receive data
                            bytes_received = 0
                            with open(unique_filename, 'wb') as f:
                                with tqdm(total=file_size, unit='B', unit_scale=True, 
                                         desc=f"Receiving {filename} on port {port}") as pbar:
                                    
                                    # First receive the length of the encrypted data
                                    length_bytes = conn.recv(4)
                                    if not length_bytes:
                                        continue
                                            
                                    length = int.from_bytes(length_bytes, 'big')
                                    
                                    # Then receive the encrypted data
                                    encrypted_data = b''
                                    while len(encrypted_data) < length:
                                        chunk = conn.recv(min(length - len(encrypted_data), self.chunk_size))
                                        if not chunk:
                                            break
                                        encrypted_data += chunk
                                        
                                        # Update progress based on received encrypted data
                                        pbar.update(len(chunk))
                                    
                                    # Decrypt the data
                                    data = decrypt_data(encrypted_data)
                                    if data:
                                        f.write(data)
                                        bytes_received = len(data)
                            
                            # Send completion acknowledgment
                            conn.send(b"COMPLETE")
                            
                            print(f"\nReceived {bytes_received / 1024:.2f} KB on port {port}")
                    except Exception as e:
                        print(f"Error in receiver thread (port {port}): {e}")
                        
        except Exception as e:
            print(f"Fatal error in receiver thread (port {port}): {e}")
            
    def get_active_receivers(self) -> Set[Tuple[str, int]]:
        """
        Get the currently active receivers
        
        Returns:
            Set of (host, port) tuples of active receivers
        """
        with self.status_lock:
            return self.active_receivers.copy() 