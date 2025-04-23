import unittest
import os
import time
import socket
import threading
import tempfile
import random
import string
import shutil
import sys
from typing import Tuple, Dict, Any

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from transfer_modes.normal_mode import NormalMode
from transfer_modes.token_bucket_mode import TokenBucketMode
from transfer_modes.aimd_mode import AIMDMode
from transfer_modes.qos_mode import QoSMode
from transfer_modes.parallel_mode import ParallelMode
from transfer_modes.multicast_mode import MulticastMode

def random_string(length: int) -> str:
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

class TestTransferModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = "127.0.0.1"
        cls.base_port = 55000  # Base port for tests
        cls.test_file_sizes = [1024, 10240, 102400]  # Test with different file sizes: 1KB, 10KB, 100KB
        
        # Create test files with random data
        cls.test_files = {}
        for size in cls.test_file_sizes:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, 'w') as f:
                f.write(random_string(size))
            cls.test_files[size] = path
    
    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        for path in cls.test_files.values():
            if os.path.exists(path):
                os.remove(path)
        
        # Clean up received files
        for f in os.listdir('.'):
            if f.startswith('received_test_'):
                try:
                    os.remove(f)
                except:
                    pass
    
    def start_receiver(self, mode_instance, event):
        result = mode_instance.receive_file()
        event.set()
        return result
    
    def test_normal_mode(self):
        print("\n--- Testing Normal Mode ---")
        port = self.base_port
        
        for size, file_path in self.test_files.items():
            # Create a temporary filename in the current directory
            temp_filename = f"test_{size}.txt"
            # Copy instead of rename to avoid cross-device link error
            shutil.copy(file_path, temp_filename)
            
            try:
                # Create instances
                sender_mode = NormalMode(self.host, port)
                receiver_mode = NormalMode(self.host, port)
                
                # Start receiver in a thread
                done_event = threading.Event()
                receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                receiver_thread.start()
                
                # Give the receiver a moment to start
                time.sleep(0.5)
                
                # Send file
                success = sender_mode.send_file(temp_filename, self.host, port)
                
                # Wait for receiver to complete
                done_event.wait(timeout=10)
                
                # Verify results
                self.assertTrue(success, f"Failed to send file of size {size}")
                self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for size {size}")
                
                # Verify file size
                received_size = os.path.getsize(f"received_{temp_filename}")
                self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
            finally:
                # Clean up - remove the temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            
            # Increment port for next test
            port += 1
    
    def test_token_bucket_mode(self):
        print("\n--- Testing Token Bucket Mode ---")
        port = self.base_port + 100
        
        for size, file_path in self.test_files.items():
            # Create a temporary filename in the current directory
            temp_filename = f"test_{size}.txt"
            # Copy instead of rename to avoid cross-device link error
            shutil.copy(file_path, temp_filename)
            
            try:
                # Create instances with much higher rate limits for faster testing
                bucket_size = 102400  # Higher bucket size
                token_rate = 102400   # Higher token rate
                sender_mode = TokenBucketMode(self.host, port, bucket_size=bucket_size, token_rate=token_rate)
                receiver_mode = TokenBucketMode(self.host, port, bucket_size=bucket_size, token_rate=token_rate)
                
                # Start receiver in a thread
                done_event = threading.Event()
                receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                receiver_thread.start()
                
                # Give the receiver a moment to start
                time.sleep(0.5)
                
                # Send file
                success = sender_mode.send_file(temp_filename, self.host, port)
                
                # Wait for receiver to complete
                done_event.wait(timeout=15)
                
                # Verify results
                self.assertTrue(success, f"Failed to send file of size {size} with Token Bucket Mode")
                self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for size {size}")
                
                # Verify file size
                received_size = os.path.getsize(f"received_{temp_filename}")
                self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
            finally:
                # Clean up - remove the temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            
            # Increment port for next test
            port += 1
    
    def test_aimd_mode(self):
        print("\n--- Testing AIMD Mode ---")
        port = self.base_port + 200
        
        for size, file_path in self.test_files.items():
            # Create a temporary filename in the current directory
            temp_filename = f"test_{size}.txt"
            # Copy instead of rename to avoid cross-device link error
            shutil.copy(file_path, temp_filename)
            
            try:
                # Create instances
                sender_mode = AIMDMode(self.host, port)
                receiver_mode = AIMDMode(self.host, port)
                
                # Start receiver in a thread
                done_event = threading.Event()
                receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                receiver_thread.start()
                
                # Give the receiver a moment to start
                time.sleep(0.5)
                
                # Send file
                success = sender_mode.send_file(temp_filename, self.host, port)
                
                # Wait for receiver to complete
                done_event.wait(timeout=15)
                
                # Verify results
                self.assertTrue(success, f"Failed to send file of size {size} with AIMD Mode")
                self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for size {size}")
                
                # Verify file size
                received_size = os.path.getsize(f"received_{temp_filename}")
                self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
            finally:
                # Clean up - remove the temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            
            # Increment port for next test
            port += 1
    
    def test_qos_mode(self):
        print("\n--- Testing QoS Mode ---")
        port = self.base_port + 300
        
        priorities = ["high", "normal", "low"]
        
        for size, file_path in self.test_files.items():
            for priority in priorities:
                # Create a temporary filename in the current directory
                temp_filename = f"test_{size}_{priority}.txt"
                # Copy instead of rename to avoid cross-device link error
                shutil.copy(file_path, temp_filename)
                
                try:
                    # Create instances
                    sender_mode = QoSMode(self.host, port)
                    receiver_mode = QoSMode(self.host, port)
                    
                    # Start receiver in a thread
                    done_event = threading.Event()
                    receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                    receiver_thread.start()
                    
                    # Give the receiver a moment to start
                    time.sleep(0.5)
                    
                    # Send file with the specific priority
                    success = sender_mode.send_file(temp_filename, self.host, port, priority=priority)
                    
                    # Wait for receiver to complete
                    done_event.wait(timeout=15)
                    
                    # Verify results
                    self.assertTrue(success, f"Failed to send file of size {size} with QoS Mode priority={priority}")
                    self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for size {size}")
                    
                    # Verify file size
                    received_size = os.path.getsize(f"received_{temp_filename}")
                    self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
                finally:
                    # Clean up - remove the temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                
                # Increment port for next test
                port += 1
    
    def test_parallel_mode(self):
        print("\n--- Testing Parallel Mode ---")
        port = self.base_port + 400
        
        thread_counts = [2, 4]
        
        for size, file_path in self.test_files.items():
            for num_threads in thread_counts:
                # Create a temporary filename in the current directory
                temp_filename = f"test_{size}_threads_{num_threads}.txt"
                # Copy instead of rename to avoid cross-device link error
                shutil.copy(file_path, temp_filename)
                
                try:
                    # Create instances
                    sender_mode = ParallelMode(self.host, port, num_threads=num_threads)
                    receiver_mode = ParallelMode(self.host, port, num_threads=num_threads)
                    
                    # Start receiver in a thread
                    done_event = threading.Event()
                    receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                    receiver_thread.start()
                    
                    # Give the receiver a moment to start
                    time.sleep(0.5)
                    
                    # Send file
                    success = sender_mode.send_file(temp_filename, self.host, port, num_threads=num_threads)
                    
                    # Wait for receiver to complete
                    done_event.wait(timeout=20)
                    
                    # Verify results
                    self.assertTrue(success, f"Failed to send file of size {size} with Parallel Mode threads={num_threads}")
                    self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for size {size}")
                    
                    # Verify file size
                    received_size = os.path.getsize(f"received_{temp_filename}")
                    self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
                finally:
                    # Clean up - remove the temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                
                # Increment port for next test
                port += 1

    def test_multicast_mode(self):
        print("\n--- Testing Multicast Mode ---")
        base_port = self.base_port + 500
        
        # Create a small file to test with just the first size
        size = self.test_file_sizes[0]  # Use the smallest test file
        file_path = self.test_files[size]
        
        # Create a temporary filename in the current directory
        temp_filename = f"test_{size}_multicast.txt"
        # Copy instead of rename to avoid cross-device link error
        shutil.copy(file_path, temp_filename)
        
        try:
            # Set up multiple receivers on different ports
            num_receivers = 3
            receiver_ports = [base_port + i for i in range(num_receivers)]
            receivers = []
            receiver_threads = []
            done_events = []
            
            # Create receivers
            for i, port in enumerate(receiver_ports):
                receiver = MulticastMode(self.host, port)
                receivers.append(receiver)
                
                # Create event for this receiver
                done_event = threading.Event()
                done_events.append(done_event)
                
                # Create and start receiver threads
                thread = threading.Thread(
                    target=self.start_receiver, 
                    args=(receiver, done_event),
                    daemon=True
                )
                receiver_threads.append(thread)
                thread.start()
            
            # Give receivers time to start
            time.sleep(1)
            
            # Create sender
            sender = MulticastMode(self.host, base_port)
            
            # Create list of targets
            targets = [(self.host, port) for port in receiver_ports]
            
            # Send to all targets
            success = sender.send_file(temp_filename, targets)
            
            # Wait for receivers to complete (up to 10 seconds)
            for event in done_events:
                event.wait(timeout=10)
            
            # Verify results
            self.assertTrue(success, f"Failed to send file via multicast")
            
            # Check all received files exist
            for i in range(num_receivers):
                received_filename = f"received_{temp_filename}"
                self.assertTrue(os.path.exists(received_filename), 
                               f"Received file not found")
                
                # Verify file size
                if os.path.exists(received_filename):
                    received_size = os.path.getsize(received_filename)
                    self.assertEqual(size, received_size, 
                                   f"Received file size {received_size} doesn't match original {size}")
        finally:
            # Clean up temporary files
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

if __name__ == "__main__":
    unittest.main() 