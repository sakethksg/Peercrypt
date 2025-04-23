import socket
import os
import time
import threading
from typing import Tuple, Optional
from src.utils.encryption import encrypt_data, decrypt_data
from tqdm import tqdm

class ParallelMode:
    def __init__(self, host: str, port: int, num_threads: int = 4):
        self.host = host
        self.port = port
        self.default_num_threads = num_threads
        self.chunk_size = 8192  # 8KB chunks
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _connect_with_retry(self, target_host: str, target_port: int, thread_id: int) -> Optional[socket.socket]:
        """Attempt to connect with retries."""
        for attempt in range(self.max_retries):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)  # 5 second timeout
                s.connect((target_host, target_port + thread_id))
                return s
            except (socket.error, ConnectionRefusedError) as e:
                print(f"Connection attempt {attempt + 1} failed for thread {thread_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                s.close()
        return None

    def send_file(self, filepath: str, target_host: str, target_port: int, num_threads: int = None) -> bool:
        try:
            # Use provided num_threads or default
            num_threads = num_threads if num_threads is not None else self.default_num_threads
            
            file_size = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            # Calculate chunk sizes
            chunk_size = file_size // num_threads
            if file_size % num_threads != 0:
                chunk_size += 1
            
            # Create progress bar
            pbar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Sending {filename}")
            
            def send_chunk(start_pos: int, end_pos: int, thread_id: int):
                try:
                    s = self._connect_with_retry(target_host, target_port, thread_id)
                    if s is None:
                        print(f"Failed to connect for thread {thread_id} after {self.max_retries} attempts")
                        return
                        
                    with s:
                        # Send chunk info
                        s.send(f"{filename}:{start_pos}:{end_pos}".encode())
                        ack = s.recv(1024)
                        if ack != b"OK":
                            print(f"Invalid acknowledgment from thread {thread_id}")
                            return
                        
                        # Send chunk data
                        with open(filepath, 'rb') as f:
                            f.seek(start_pos)
                            remaining = end_pos - start_pos
                            while remaining > 0:
                                data = f.read(min(self.chunk_size, remaining))
                                if not data:
                                    break
                                encrypted_data = encrypt_data(data)
                                # Send length first
                                s.send(len(encrypted_data).to_bytes(4, 'big'))
                                # Then send the data
                                s.send(encrypted_data)
                                pbar.update(len(data))
                                remaining -= len(data)
                                
                                # Wait for acknowledgment
                                ack = s.recv(1024)
                                if ack != b"OK":
                                    print(f"Transfer failed in thread {thread_id}")
                                    return
                except Exception as e:
                    print(f"Error in thread {thread_id}: {e}")

            # Start threads
            threads = []
            start_time = time.time()
            
            for i in range(num_threads):
                start_pos = i * chunk_size
                end_pos = min((i + 1) * chunk_size, file_size)
                if start_pos >= file_size:
                    break
                    
                t = threading.Thread(target=send_chunk, args=(start_pos, end_pos, i))
                threads.append(t)
                t.start()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            pbar.close()
            transfer_time = time.time() - start_time
            speed = file_size / transfer_time / 1024  # KB/s
            print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
            return True
        except Exception as e:
            print(f"Error sending file: {e}")
            return False

    def receive_file(self) -> Tuple[bool, Optional[str]]:
        try:
            # Create a socket for each thread
            sockets = []
            for i in range(self.default_num_threads):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port + i))
                s.listen(1)
                sockets.append(s)
            
            # Dictionary to store received chunks
            chunks = {}
            filename = None
            total_size = 0
            
            def receive_chunk(sock: socket.socket, thread_id: int):
                nonlocal filename, total_size
                try:
                    conn, addr = sock.accept()
                    with conn:
                        # Receive chunk info
                        info = conn.recv(1024).decode()
                        filename, start_pos, end_pos = info.split(':')
                        start_pos = int(start_pos)
                        end_pos = int(end_pos)
                        conn.send(b"OK")
                        
                        # Create progress bar for this chunk
                        chunk_size = end_pos - start_pos
                        pbar = tqdm(total=chunk_size, unit='B', unit_scale=True, 
                                  desc=f"Receiving chunk {thread_id}", position=thread_id)
                        
                        # Receive chunk data
                        temp_file = f"chunk_{thread_id}_{filename}"
                        with open(temp_file, 'wb') as f:
                            bytes_received = 0
                            while bytes_received < chunk_size:
                                # Receive length
                                length_bytes = conn.recv(4)
                                if not length_bytes:
                                    break
                                length = int.from_bytes(length_bytes, 'big')
                                
                                # Receive data
                                encrypted_data = b''
                                while len(encrypted_data) < length:
                                    chunk = conn.recv(min(length - len(encrypted_data), self.chunk_size))
                                    if not chunk:
                                        break
                                    encrypted_data += chunk
                                    
                                if not encrypted_data:
                                    break
                                    
                                data = decrypt_data(encrypted_data)
                                if data:
                                    f.write(data)
                                    bytes_received += len(data)
                                    pbar.update(len(data))
                                    conn.send(b"OK")  # Send acknowledgment
                        
                        pbar.close()
                        chunks[start_pos] = temp_file
                except Exception as e:
                    print(f"Error in receive thread {thread_id}: {e}")
            
            # Start receiving threads
            threads = []
            for i, sock in enumerate(sockets):
                t = threading.Thread(target=receive_chunk, args=(sock, i))
                threads.append(t)
                t.start()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            # Close all sockets
            for sock in sockets:
                sock.close()
            
            # Combine chunks
            if chunks:
                with open(f"received_{filename}", 'wb') as outfile:
                    for start_pos in sorted(chunks.keys()):
                        with open(chunks[start_pos], 'rb') as infile:
                            outfile.write(infile.read())
                        os.remove(chunks[start_pos])
                
                return True, f"received_{filename}"
            
            return False, None
        except Exception as e:
            print(f"Error receiving file: {e}")
            return False, None 