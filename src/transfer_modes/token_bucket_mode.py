import time
import socket
import os
import json
from typing import Tuple, Optional, Dict, Any
from threading import Thread, Lock
from utils.encryption import encrypt_data, decrypt_data
from tqdm import tqdm
from datetime import datetime

class TransferStats:
    """Track statistics for file transfers"""
    def __init__(self):
        self.start_time = time.time()
        self.bytes_transferred = 0
        self.chunks_sent = 0
        self.retries = 0
        self.errors = 0
        self.rate_history = []
        self.chunk_size_history = []
        self.last_update = time.time()

    def update(self, bytes_transferred: int, chunk_size: int, retries: int = 0, error: bool = False):
        """Update transfer statistics"""
        self.bytes_transferred += bytes_transferred
        self.chunks_sent += 1
        self.retries += retries
        if error:
            self.errors += 1
        
        current_time = time.time()
        if current_time - self.last_update >= 1.0:  # Update every second
            rate = self.bytes_transferred / (current_time - self.start_time) / 1024  # KB/s
            self.rate_history.append((current_time, rate))
            self.chunk_size_history.append((current_time, chunk_size))
            self.last_update = current_time

    def get_stats(self) -> Dict[str, Any]:
        """Get current transfer statistics"""
        duration = time.time() - self.start_time
        avg_rate = self.bytes_transferred / duration / 1024 if duration > 0 else 0
        return {
            "duration": duration,
            "bytes_transferred": self.bytes_transferred,
            "chunks_sent": self.chunks_sent,
            "retries": self.retries,
            "errors": self.errors,
            "average_rate": avg_rate,
            "rate_history": self.rate_history,
            "chunk_size_history": self.chunk_size_history
        }

class TokenBucket:
    """A token bucket implementation for rate limiting"""
    def __init__(self, capacity: int, rate: float):
        """
        Initialize a token bucket
        
        Args:
            capacity: Maximum number of tokens the bucket can hold
            rate: Rate at which tokens are added to the bucket (tokens/second)
        """
        self.capacity = capacity
        self.rate = rate
        self.tokens = capacity  # Start with a full bucket
        self.last_update = time.time()
        
        # Pre-fill the bucket for quick start
        self._update_tokens()
    
    def _update_tokens(self) -> None:
        """Update the token count based on elapsed time"""
        now = time.time()
        time_passed = now - self.last_update
        if time_passed > 0:
            new_tokens = time_passed * self.rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_update = now
    
    def consume(self, tokens: int) -> bool:
        """
        Try to consume tokens from the bucket
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were successfully consumed, False otherwise
        """
        self._update_tokens()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def get_wait_time(self, tokens: int) -> float:
        """
        Calculate wait time until enough tokens are available
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Time in seconds to wait for tokens to become available
        """
        self._update_tokens()
        
        if self.tokens >= tokens:
            return 0
        
        additional_tokens_needed = tokens - self.tokens
        return additional_tokens_needed / self.rate
    
    def get_available_tokens(self) -> int:
        """Get the current number of available tokens"""
        self._update_tokens()
        return int(self.tokens)

class TokenBucketMode:
    """File transfer mode using token bucket rate limiting"""
    def __init__(self, host: str, port: int, bucket_size: int = 1024, token_rate: float = 100):
        """
        Initialize token bucket transfer mode
        
        Args:
            host: Host address to bind to
            port: Port to bind to
            bucket_size: Maximum tokens in the bucket
            token_rate: Rate of token replenishment (tokens/sec)
        """
        self.host = host
        self.port = port
        self.chunk_size = 8192  # 8KB chunks
        self.default_bucket_size = bucket_size
        self.default_token_rate = token_rate
        self.bucket = TokenBucket(bucket_size, token_rate)
        
        # Each token represents 1KB
        self.tokens_per_chunk = max(1, self.chunk_size // 1024)
        
        self.stats = TransferStats()
        self.ack_timeout = 5.0  # seconds
    
    def save_stats(self, filename: str) -> None:
        """
        Save transfer statistics to a JSON file
        
        Args:
            filename: Base filename to use for the stats file
        """
        stats = self.stats.get_stats()
        stats["timestamp"] = datetime.now().isoformat()
        stats["mode"] = "token-bucket"
        stats["bucket_size"] = self.bucket.capacity
        stats["token_rate"] = self.bucket.rate
        
        try:
            with open(f"transfer_stats_{filename}.json", "w") as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def _wait_for_tokens(self, tokens_needed: int, max_wait: float = 1.0) -> bool:
        """
        Wait until tokens are available or max_wait is reached
        
        Args:
            tokens_needed: Number of tokens needed
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if tokens are available, False if max_wait was reached
        """
        wait_time = self.bucket.get_wait_time(tokens_needed)
        
        if wait_time <= 0:
            return self.bucket.consume(tokens_needed)
        
        if wait_time <= max_wait:
            time.sleep(wait_time)
            return self.bucket.consume(tokens_needed)
        
        return False
    
    def send_file(self, filepath: str, target_host: str, target_port: int, **kwargs) -> bool:
        """
        Send a file using token bucket rate limiting
        
        Args:
            filepath: Path to the file to send
            target_host: Destination host address
            target_port: Destination port
            **kwargs: Additional options:
                - bucket_size: Override default bucket size
                - token_rate: Override default token rate
                
        Returns:
            True if the file was sent successfully, False otherwise
        """
        # Reset stats
        self.stats = TransferStats()
        
        # Apply override parameters if provided
        bucket_size = kwargs.get('bucket_size', self.default_bucket_size)
        token_rate = kwargs.get('token_rate', self.default_token_rate)
        self.bucket = TokenBucket(bucket_size, token_rate)
        
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
                
                # Send file data with rate limiting
                bytes_sent = 0
                with open(filepath, 'rb') as f:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Sending {filename}") as pbar:
                        while bytes_sent < file_size:
                            # Calculate optimal chunk size
                            remaining = file_size - bytes_sent
                            chunk_size = min(self.chunk_size, remaining)
                            tokens_needed = max(1, chunk_size // 1024)
                            
                            # Wait for tokens to be available
                            if not self._wait_for_tokens(tokens_needed):
                                # If we can't get tokens, use a smaller chunk size
                                tokens_available = self.bucket.get_available_tokens()
                                if tokens_available > 0:
                                    chunk_size = tokens_available * 1024
                                    tokens_needed = tokens_available
                                    self.bucket.consume(tokens_needed)
                                else:
                                    # If no tokens available, wait a bit and try again
                                    time.sleep(0.1)
                                    continue
                            
                            # Read and send data
                            data = f.read(chunk_size)
                            if not data:
                                break
                                
                            encrypted_data = encrypt_data(data)
                            
                            # Send length of encrypted data first
                            s.send(len(encrypted_data).to_bytes(4, 'big'))
                            # Then send the encrypted data
                            s.send(encrypted_data)
                            
                            # Wait for acknowledgment
                            try:
                                s.settimeout(self.ack_timeout)
                                ack = s.recv(1)
                                if ack != b'1':
                                    raise Exception("Invalid acknowledgment received")
                            except socket.timeout:
                                raise Exception("Acknowledgment timeout")
                            
                            # Update progress and stats
                            bytes_sent += len(data)
                            pbar.update(len(data))
                            self.stats.update(len(data), chunk_size)
                
                transfer_time = time.time() - self.stats.start_time
                speed = file_size / transfer_time / 1024  # KB/s
                print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                
                # Save transfer statistics
                self.save_stats(filename)
                
                return True
                
        except Exception as e:
            print(f"Error sending file: {e}")
            return False
    
    def receive_file(self) -> Tuple[bool, Optional[str]]:
        """
        Receive a file using token bucket rate limiting
        
        Returns:
            Tuple of (success_flag, filename_if_successful)
        """
        # Reset stats
        self.stats = TransferStats()
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen(1)
                
                print(f"Waiting for connection on {self.host}:{self.port}...")
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                
                with conn:
                    # Receive filename
                    filename = conn.recv(1024).decode()
                    conn.send(b"OK")
                    
                    # Receive file size
                    file_size = int(conn.recv(1024).decode())
                    conn.send(b"OK")
                    
                    # Receive file data
                    bytes_received = 0
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
                                
                                # Rate limit the receiving side too
                                tokens_needed = max(1, len(encrypted_data) // 1024)
                                self._wait_for_tokens(tokens_needed, max_wait=0.1)
                                
                                # Decrypt and write data
                                data = decrypt_data(encrypted_data)
                                if data:
                                    f.write(data)
                                    bytes_received += len(data)
                                    pbar.update(len(data))
                                    self.stats.update(len(data), len(encrypted_data))
                                
                                # Send acknowledgment
                                conn.send(b'1')
                    
                    transfer_time = time.time() - self.stats.start_time
                    speed = file_size / transfer_time / 1024  # KB/s
                    print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                    
                    # Save transfer statistics
                    self.save_stats(filename)
                    
                    return True, f"received_{filename}"
                    
        except Exception as e:
            print(f"Error receiving file: {e}")
            return False, None 