import socket
import os
import time
from typing import Tuple, Optional
from src.utils.encryption import encrypt_data, decrypt_data
from tqdm import tqdm

class NormalMode:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.chunk_size = 8192  # 8KB chunks

    def send_file(self, filepath: str, target_host: str, target_port: int) -> bool:
        try:
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
                
                # Send file data with progress bar
                start_time = time.time()
                with open(filepath, 'rb') as f:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Sending {filename}") as pbar:
                        while True:
                            data = f.read(self.chunk_size)
                            if not data:
                                break
                            encrypted_data = encrypt_data(data)
                            # Send length of encrypted data first
                            s.send(len(encrypted_data).to_bytes(4, 'big'))
                            # Then send the encrypted data
                            s.send(encrypted_data)
                            pbar.update(len(data))
                
                transfer_time = time.time() - start_time
                speed = file_size / transfer_time / 1024  # KB/s
                print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                return True
        except Exception as e:
            print(f"Error sending file: {e}")
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
                    
                    # Receive and write file data with progress bar
                    start_time = time.time()
                    with open(f"received_{filename}", 'wb') as f:
                        bytes_received = 0
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
                                    
                                data = decrypt_data(encrypted_data)
                                if data:
                                    f.write(data)
                                    bytes_received += len(data)
                                    pbar.update(len(data))
                    
                    transfer_time = time.time() - start_time
                    speed = file_size / transfer_time / 1024  # KB/s
                    print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                    return True, f"received_{filename}"
        except Exception as e:
            print(f"Error receiving file: {e}")
            return False, None 