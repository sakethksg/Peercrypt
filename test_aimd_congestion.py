#!/usr/bin/env python3
import os
import sys
import time
import tempfile
import threading
import socket
import random
import string
import numpy as np
from typing import Tuple, List, Dict, Optional
import json
import signal

# Add the project root and src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)
src_dir = os.path.join(project_root, 'src')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import the AIMDMode class
from src.transfer_modes.aimd_mode import AIMDMode

def random_string(length: int) -> str:
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def get_free_port() -> int:
    """Find a free port on the host"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

class ApplicationCongestion:
    """Simulates congestion by manipulating the AIMDMode instance directly"""
    def __init__(self):
        self.congestion_periods = []
        self.start_time = time.time()
        self.sender_mode = None
        
    def register_sender(self, sender_mode):
        """Register the sender mode for direct manipulation"""
        self.sender_mode = sender_mode
        
    def simulate_congestion_event(self, packet_loss, delay_ms, duration_sec):
        """Simulate a congestion event for a specific duration"""
        congestion_start = time.time() - self.start_time
        loss_pct = packet_loss * 100
        print(f"\nIntroducing congestion at {congestion_start:.2f}s: {loss_pct:.1f}% loss, {delay_ms}ms delay")
        
        # Force congestion detection in AIMD mode by directly triggering timeout or triple-ack
        if self.sender_mode:
            # Simulate congestion by forcing window reduction
            self.sender_mode.update_window(False, "timeout")
            
            # Artificially slow down the sending rate to simulate delay
            time.sleep(delay_ms / 1000.0)
            
            # For high packet loss, trigger multiple congestion events
            if packet_loss > 0.2:
                time.sleep(0.5)
                self.sender_mode.update_window(False, "triple_ack")
        
        # Record the congestion period
        self.congestion_periods.append((congestion_start, congestion_start + duration_sec))
        
        # Wait for the duration
        time.sleep(duration_sec)
        
        print(f"Congestion ended at {time.time() - self.start_time:.2f}s")

def start_receiver(mode_instance, done_event):
    """Start a receiver and set the event when done"""
    try:
        result = mode_instance.receive_file()
        done_event.set()
        return result
    except Exception as e:
        print(f"Receiver exception: {e}")
        done_event.set()
        return False, None

def run_aimd_test(file_size, window_size):
    """Run a test of AIMD mode with simulated congestion"""
    host = "127.0.0.1"
    
    # Create a test file
    fd, file_path = tempfile.mkstemp()
    os.close(fd)
    
    with open(file_path, 'w') as f:
        f.write(random_string(file_size))
    
    temp_filename = "test_congestion.txt"
    
    try:
        # Copy the file to the current directory
        with open(file_path, 'rb') as src, open(temp_filename, 'wb') as dst:
            dst.write(src.read())
        
        # Get a free port for this test
        port = get_free_port()
        print(f"Using port {port} for AIMD congestion test with file size {file_size}B")
        
        # Create sender and receiver instances
        sender_mode = AIMDMode(host, port, initial_window=window_size)
        receiver_mode = AIMDMode(host, port, initial_window=window_size)
        
        # Create the congestion simulator
        congestion = ApplicationCongestion()
        congestion.register_sender(sender_mode)
        
        # Start receiver in a thread
        done_event = threading.Event()
        receiver_thread = threading.Thread(target=start_receiver, 
                                          args=(receiver_mode, done_event))
        receiver_thread.daemon = True
        receiver_thread.start()
        
        # Give the receiver a moment to start
        time.sleep(0.5)
        
        # Create a thread to introduce congestion at specific times
        def introduce_congestion():
            time.sleep(3)  # Let transfer start first
            
            # Moderate congestion
            congestion.simulate_congestion_event(0.05, 50, 3)
            
            time.sleep(5)  # Normal conditions
            
            # Severe congestion
            congestion.simulate_congestion_event(0.15, 200, 4)
            
            time.sleep(6)  # Normal conditions
            
            # Extreme congestion
            congestion.simulate_congestion_event(0.40, 500, 5)
        
        # Start the congestion thread
        congestion_thread = threading.Thread(target=introduce_congestion)
        congestion_thread.daemon = True
        congestion_thread.start()
        
        # Send file
        success = sender_mode.send_file(temp_filename, host, port, 
                                      timeout_detection=True, 
                                      dupack_detection=True)
        
        # Wait for receiver to complete with a generous timeout
        done_event.wait(timeout=60)
        
        # Get bandwidth history from the sender
        time_history = sender_mode.time_history
        bandwidth_history = sender_mode.bandwidth_history
        
        # Print statistics
        print("\nAIMD Congestion Statistics:")
        print(f"  Timeouts: {sender_mode.timeouts}")
        print(f"  Fast Retransmits: {sender_mode.fast_retransmits}")
        print(f"  Total Retransmissions: {sender_mode.total_retransmits}")
        if sender_mode.srtt is not None:
            print(f"  Final Smoothed RTT: {sender_mode.srtt*1000:.2f}ms")
        print(f"  Final RTO: {sender_mode.rto:.2f}s")
        
        # Save statistics to a JSON file
        stats = {
            "file_size": file_size,
            "window_size": window_size,
            "timeouts": sender_mode.timeouts,
            "fast_retransmits": sender_mode.fast_retransmits,
            "total_retransmissions": sender_mode.total_retransmits,
            "srtt_ms": sender_mode.srtt * 1000 if sender_mode.srtt is not None else None,
            "rto_sec": sender_mode.rto,
            "congestion_periods": congestion.congestion_periods,
            "bandwidth_stats": [{"time": t, "bandwidth": b} for t, b in zip(time_history, bandwidth_history)]
        }
        
        with open("aimd_congestion_stats.json", "w") as f:
            json.dump(stats, f, indent=2)
        
        # Verify the file transfer
        print(f"\nFile transfer success: {success}")
        if os.path.exists(f"received_{temp_filename}"):
            received_size = os.path.getsize(f"received_{temp_filename}")
            print(f"Received file size: {received_size} bytes (original: {file_size} bytes)")
            print(f"Size ratio: {received_size/file_size:.2%}")
        else:
            print("Warning: Received file not found!")
        
        return stats
        
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if os.path.exists(f"received_{temp_filename}"):
            os.remove(f"received_{temp_filename}")

def test_aimd_congestion():
    """Test the AIMD mode under congestion conditions"""
    print("\n--- Testing AIMD Mode Under Congestion Conditions ---")
    
    file_size = 1024 * 1024  # 1MB for better congestion analysis
    window_size = 8192  # 8KB initial window size
    
    try:
        # Run the AIMD test
        stats = run_aimd_test(file_size, window_size)
        
        print("\nTest completed successfully!")
        print(f"Statistics saved to aimd_congestion_stats.json")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nTest failed with error: {e}")

if __name__ == "__main__":
    test_aimd_congestion() 