import time
import socket
import os
import threading
import numpy as np
from typing import Tuple, Optional, List, Dict
from tqdm import tqdm

class AIMDMode:
    def __init__(self, host: str, port: int, initial_window: int = 1024):
        self.host = host
        self.port = port
        self.chunk_size = 8192
        self.window_size = initial_window
        self.min_window = 1024
        self.max_window = 65536
        self.bandwidth_history: List[float] = []
        self.time_history: List[float] = []
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.should_plot = False  # Disable plotting by default
        
        # Congestion detection parameters
        self.rto = 1.0  # Initial retransmission timeout in seconds
        self.srtt = None  # Smoothed round-trip time
        self.rttvar = None  # Round-trip time variation
        self.alpha = 0.125  # SRTT smoothing factor
        self.beta = 0.25  # RTTVAR smoothing factor
        self.dup_acks = 0  # Count of duplicate ACKs
        self.dup_ack_threshold = 3  # Triple duplicate ACK threshold
        self.timeout_enabled = True  # Enable timeout-based congestion detection
        self.dupack_enabled = True   # Enable duplicate ACK-based congestion detection
        self.last_ack = -1  # Last acknowledged sequence number
        self.next_seq = 0  # Next sequence number to send
        self.sequence_to_time: Dict[int, float] = {}  # Mapping sequence to send time
        self.last_recovery = 0  # Last sequence number that triggered recovery
        self.in_fast_recovery = False  # Fast recovery state
        
        # Statistics
        self.timeouts = 0
        self.fast_retransmits = 0
        self.total_retransmits = 0

    def update_window(self, success: bool, reason: str = ""):
        with self.lock:
            if success:
                # Additive Increase
                self.window_size = min(self.max_window, self.window_size + 1024)
            else:
                # Multiplicative Decrease
                self.window_size = max(self.min_window, self.window_size // 2)
                if reason == "timeout":
                    self.timeouts += 1
                elif reason == "triple_ack":
                    self.fast_retransmits += 1
                self.total_retransmits += 1
                
            # Log congestion event
            if not success:
                current_time = time.time() - self.start_time
                print(f"\r[{current_time:.2f}s] Congestion detected ({reason}). Window: {self.window_size//1024}KB", end="")

    def update_bandwidth(self, bytes_transferred: int):
        current_time = time.time() - self.start_time
        bandwidth = bytes_transferred / current_time if current_time > 0 else 0  # bytes per second
        
        with self.lock:
            self.bandwidth_history.append(bandwidth / 1024)  # Convert to KB/s
            self.time_history.append(current_time)
            print(f"\rCurrent bandwidth: {bandwidth/1024:.2f} KB/s | Window: {self.window_size//1024} KB", end="")

    def update_rtt(self, rtt: float, sequence: int):
        """Update RTT statistics using Jacobson/Karels algorithm"""
        if self.srtt is None:
            # First RTT measurement
            self.srtt = rtt
            self.rttvar = rtt / 2
        else:
            # Update RTTVAR and SRTT
            self.rttvar = (1 - self.beta) * self.rttvar + self.beta * abs(self.srtt - rtt)
            self.srtt = (1 - self.alpha) * self.srtt + self.alpha * rtt
        
        # Update RTO
        self.rto = self.srtt + 4 * self.rttvar
        # Ensure RTO is at least 1 second and not too large
        self.rto = max(1.0, min(self.rto, 60.0))

    def handle_ack(self, ack_seq: int) -> Tuple[bool, str]:
        """Handle acknowledgment packet and detect congestion
        Returns (retransmit_needed, reason)
        """
        with self.lock:
            # Measure RTT if this ACK corresponds to a tracked sequence
            if ack_seq in self.sequence_to_time:
                send_time = self.sequence_to_time[ack_seq]
                rtt = time.time() - send_time
                self.update_rtt(rtt, ack_seq)
                del self.sequence_to_time[ack_seq]
            
            # Check for duplicate ACKs
            if ack_seq == self.last_ack and self.dupack_enabled:
                self.dup_acks += 1
                if self.dup_acks >= self.dup_ack_threshold:
                    # Triple duplicate ACK - indicate congestion
                    self.dup_acks = 0
                    if not self.in_fast_recovery and self.last_recovery != ack_seq:
                        self.in_fast_recovery = True
                        self.last_recovery = ack_seq
                        return True, "triple_ack"
            elif ack_seq > self.last_ack:
                # New ACK
                self.dup_acks = 0
                self.last_ack = ack_seq
                
                # Exit fast recovery if applicable
                if self.in_fast_recovery and ack_seq > self.last_recovery:
                    self.in_fast_recovery = False
            
            return False, ""

    def check_timeouts(self) -> Tuple[bool, Optional[int]]:
        """Check for timeouts in unacknowledged packets
        Returns (timeout_occurred, sequence_to_retransmit)
        """
        if not self.timeout_enabled:
            return False, None
            
        current_time = time.time()
        with self.lock:
            for seq, send_time in list(self.sequence_to_time.items()):
                if current_time - send_time > self.rto:
                    # Timeout detected
                    return True, seq
                    
        return False, None

    def export_stats(self, filename: str = 'bandwidth_stats.csv'):
        with self.lock:
            data = np.column_stack((self.time_history, self.bandwidth_history))
            np.savetxt(filename, data, delimiter=',', header='Time(s),Bandwidth(KB/s)')
            print(f"\nBandwidth statistics saved to {filename}")
            
            # Additional congestion statistics
            print(f"Congestion events:")
            print(f"  Timeouts: {self.timeouts}")
            print(f"  Fast Retransmits: {self.fast_retransmits}")
            print(f"  Total Retransmissions: {self.total_retransmits}")
            print(f"  Final RTO: {self.rto:.2f}s")
            if self.srtt is not None:
                print(f"  Smoothed RTT: {self.srtt*1000:.2f}ms")

    def send_file(self, filepath: str, target_host: str, target_port: int, **kwargs) -> bool:
        try:
            # Get congestion detection settings from kwargs
            self.timeout_enabled = kwargs.get('timeout_detection', True)
            self.dupack_enabled = kwargs.get('dupack_detection', True)
            
            # Reset sequence tracking
            self.next_seq = 0
            self.last_ack = -1
            self.dup_acks = 0
            self.sequence_to_time = {}
            self.timeouts = 0
            self.fast_retransmits = 0
            self.total_retransmits = 0
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((target_host, target_port))
                
                # Send filename
                filename = os.path.basename(filepath)
                s.send(filename.encode())
                s.recv(1024)  # Wait for acknowledgment
                
                # Send file size
                file_size = os.path.getsize(filepath)
                s.send(str(file_size).encode())
                s.recv(1024)  # Wait for acknowledgment
                
                # Send congestion detection info
                congestion_info = {
                    'timeout_detection': self.timeout_enabled,
                    'dupack_detection': self.dupack_enabled
                }
                s.send(str(congestion_info).encode())
                s.recv(1024)  # Wait for acknowledgment
                
                # Reset start time for bandwidth calculation
                self.start_time = time.time()
                self.bandwidth_history = []
                self.time_history = []
                
                # Create a non-blocking socket for receiving ACKs
                s.setblocking(False)
                
                bytes_sent = 0
                file_position = 0
                
                with open(filepath, 'rb') as f:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Sending {filename}") as pbar:
                        while bytes_sent < file_size:
                            # Check for timeouts
                            timeout_occurred, timeout_seq = self.check_timeouts()
                            if timeout_occurred:
                                # Handle timeout
                                self.update_window(False, "timeout")
                                
                                # Calculate position in file for retransmission
                                # For simplicity, we'll restart from the last ACK position
                                next_pos = max(0, self.last_ack * self.chunk_size)
                                f.seek(next_pos)
                                file_position = next_pos
                                
                                # Reset next sequence to send
                                self.next_seq = self.last_ack + 1 if self.last_ack >= 0 else 0
                                
                                # Clear timeout sequence
                                if timeout_seq in self.sequence_to_time:
                                    del self.sequence_to_time[timeout_seq]
                            
                            # Try to receive ACKs (non-blocking)
                            try:
                                ack_data = s.recv(1024)
                                if ack_data:
                                    ack_seq = int(ack_data.decode())
                                    retransmit, reason = self.handle_ack(ack_seq)
                                    
                                    if retransmit:
                                        # Fast retransmit
                                        self.update_window(False, reason)
                                        
                                        # Go back to the sequence that needs retransmission
                                        next_pos = max(0, ack_seq * self.chunk_size)
                                        f.seek(next_pos)
                                        file_position = next_pos
                                        self.next_seq = ack_seq + 1
                                    else:
                                        # Normal ACK, update window
                                        self.update_window(True)
                            except BlockingIOError:
                                # No ACK available, continue sending
                                pass
                            
                            # Calculate how many chunks we can send based on window size
                            # and ensure we're at the right position in file
                            if f.tell() != file_position:
                                f.seek(file_position)
                                
                            # Calculate current window in chunks
                            window_chunks = max(1, self.window_size // self.chunk_size)
                            
                            # Only send if we have room in our window
                            if self.next_seq < self.last_ack + 1 + window_chunks:
                                # Read data
                                data = f.read(min(self.chunk_size, file_size - file_position))
                                if not data:
                                    break
                                    
                                # Prepare packet with sequence number
                                seq_header = str(self.next_seq).encode() + b':'
                                
                                # Send the length of data first
                                s.send(len(data).to_bytes(4, 'big'))
                                
                                # Then send sequence header and data
                                s.send(seq_header + data)
                                
                                # Record send time for this sequence
                                self.sequence_to_time[self.next_seq] = time.time()
                                
                                # Update tracking
                                self.next_seq += 1
                                bytes_sent += len(data)
                                file_position += len(data)
                                pbar.update(len(data))
                                self.update_bandwidth(bytes_sent)
                            else:
                                # Wait a bit if window is full
                                time.sleep(0.01)
                
                # Wait for all ACKs to be received (go back to blocking mode)
                s.setblocking(True)
                
                # Send end of transmission marker with proper formatting
                s.send(len(b"EOT").to_bytes(4, 'big'))  # Send length first
                s.send(b"EOT")                          # Then send EOT marker
                
                transfer_time = time.time() - self.start_time
                speed = file_size / transfer_time / 1024 if transfer_time > 0 else 0
                print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                
                self.export_stats()
                return True
        except Exception as e:
            print(f"\nError sending file: {e}")
            return False

    def receive_file(self) -> Tuple[bool, Optional[str]]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen(1)
                
                # Reset start time for bandwidth calculation
                self.start_time = time.time()
                self.bandwidth_history = []
                self.time_history = []
                
                # Reset sequence tracking for receiving
                self.last_ack = -1
                
                conn, addr = s.accept()
                with conn:
                    # Receive filename
                    filename = conn.recv(1024).decode()
                    conn.send(b"OK")
                    
                    # Receive file size
                    file_size = int(conn.recv(1024).decode())
                    conn.send(b"OK")
                    
                    # Receive congestion detection settings
                    try:
                        congestion_info = conn.recv(1024).decode()
                        settings = eval(congestion_info)  # Safe since we're only expecting a dictionary
                        self.timeout_enabled = settings.get('timeout_detection', True)
                        self.dupack_enabled = settings.get('dupack_detection', True)
                        print(f"Congestion detection: Timeout={self.timeout_enabled}, DupACK={self.dupack_enabled}")
                    except:
                        # If anything goes wrong, use defaults
                        self.timeout_enabled = True
                        self.dupack_enabled = True
                    conn.send(b"OK")
                    
                    bytes_received = 0
                    expected_seq = 0
                    out_of_order_buffers = {}  # Store out-of-order packets
                    
                    with open(f"received_{filename}", 'wb') as f:
                        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Receiving {filename}") as pbar:
                            while bytes_received < file_size:
                                # First receive the length of the data
                                length_bytes = conn.recv(4)
                                if not length_bytes:
                                    break
                                    
                                length = int.from_bytes(length_bytes, 'big')
                                
                                # Then receive the data with sequence
                                packet = b''
                                while len(packet) < length:
                                    chunk = conn.recv(min(length - len(packet), self.chunk_size))
                                    if not chunk:
                                        break
                                    packet += chunk
                                
                                if not packet:
                                    # End of transmission
                                    break
                                
                                # Check for EOT marker
                                if packet == b"EOT":
                                    print("End of transmission marker received")
                                    break
                                
                                # Parse sequence number
                                colon_pos = packet.find(b':')
                                if colon_pos > 0:
                                    seq_str = packet[:colon_pos].decode()
                                    try:
                                        seq = int(seq_str)
                                        data = packet[colon_pos+1:]
                                        
                                        if seq == expected_seq:
                                            # In-order packet
                                            if data:
                                                f.write(data)
                                                bytes_received += len(data)
                                                pbar.update(len(data))
                                                self.update_bandwidth(bytes_received)
                                            
                                            # Acknowledge this packet
                                            conn.send(str(seq).encode())
                                            self.last_ack = seq
                                            expected_seq += 1
                                            
                                            # Process any buffered packets that are now in order
                                            while expected_seq in out_of_order_buffers:
                                                buffered_data = out_of_order_buffers.pop(expected_seq)
                                                f.write(buffered_data)
                                                bytes_received += len(buffered_data)
                                                pbar.update(len(buffered_data))
                                                
                                                # Acknowledge this buffered packet
                                                conn.send(str(expected_seq).encode())
                                                self.last_ack = expected_seq
                                                expected_seq += 1
                                                
                                        elif seq > expected_seq:
                                            # Out of order packet
                                            if data:
                                                # Store in buffer
                                                out_of_order_buffers[seq] = data
                                            
                                            # Send duplicate ACK for the last in-order packet
                                            conn.send(str(self.last_ack).encode())
                                        else:
                                            # Duplicate packet, acknowledge it again
                                            conn.send(str(seq).encode())
                                    except ValueError:
                                        # Invalid sequence number, ignore
                                        pass
                    
                    transfer_time = time.time() - self.start_time
                    speed = file_size / transfer_time / 1024 if transfer_time > 0 else 0
                    print(f"\nTransfer completed in {transfer_time:.2f} seconds ({speed:.2f} KB/s)")
                    
                    self.export_stats()
                    return True, f"received_{filename}"
        except Exception as e:
            print(f"Error receiving file: {e}")
            return False, None
            
    def configure(self, **kwargs):
        """Configure AIMD congestion control parameters"""
        with self.lock:
            if 'initial_window' in kwargs:
                self.window_size = int(kwargs['initial_window'])
            if 'min_window' in kwargs:
                self.min_window = int(kwargs['min_window'])
            if 'max_window' in kwargs:
                self.max_window = int(kwargs['max_window'])
            if 'timeout_enabled' in kwargs:
                self.timeout_enabled = bool(kwargs['timeout_enabled'])
            if 'dupack_enabled' in kwargs:
                self.dupack_enabled = bool(kwargs['dupack_enabled'])
            if 'dup_ack_threshold' in kwargs:
                self.dup_ack_threshold = int(kwargs['dup_ack_threshold'])
                
            return {
                'initial_window': self.window_size,
                'min_window': self.min_window,
                'max_window': self.max_window,
                'timeout_enabled': self.timeout_enabled,
                'dupack_enabled': self.dupack_enabled,
                'dup_ack_threshold': self.dup_ack_threshold
            } 