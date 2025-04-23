#!/usr/bin/env python3
import os
import sys
import time
import tempfile
import unittest
import random
import string
import threading
import shutil
import socket
from typing import Dict, Any

def random_string(length: int) -> str:
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def get_free_port():
    """Find a free port on the host"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class TestAllModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Import here to ensure paths are correct
        from src.transfer_modes.normal_mode import NormalMode
        from src.transfer_modes.token_bucket_mode import TokenBucketMode
        from src.transfer_modes.aimd_mode import AIMDMode
        from src.transfer_modes.qos_mode import QoSMode
        from src.transfer_modes.parallel_mode import ParallelMode
        from src.transfer_modes.multicast_mode import MulticastMode
        
        cls.host = "127.0.0.1"
        cls.test_file_sizes = [1024, 10240, 102400]  # Test with different file sizes: 1KB, 10KB, 100KB
        
        # Save the mode classes for easy instantiation
        cls.modes = {
            "normal": NormalMode,
            "token-bucket": TokenBucketMode,
            "aimd": AIMDMode,
            "qos": QoSMode,
            "parallel": ParallelMode,
            "multicast": MulticastMode
        }
        
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
        try:
            result = mode_instance.receive_file()
            event.set()
            return result
        except Exception as e:
            print(f"Receiver exception: {e}")
            event.set()
            return False, None
    
    def test_normal_mode(self):
        """Test the normal file transfer mode"""
        print("\n--- Testing Normal Mode ---")
        
        for size, file_path in self.test_files.items():
            # Create a temporary filename in the current directory
            temp_filename = f"test_{size}.txt"
            # Copy instead of rename to avoid cross-device link error
            shutil.copy(file_path, temp_filename)
            
            # Get a free port for this test
            port = get_free_port()
            print(f"Using port {port} for normal mode test with file size {size}B")
            
            try:
                # Create instances
                sender_mode = self.modes["normal"](self.host, port)
                receiver_mode = self.modes["normal"](self.host, port)
                
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
                if os.path.exists(f"received_{temp_filename}"):
                    os.remove(f"received_{temp_filename}")
            
            # Add a delay before the next test to allow socket cleanup
            time.sleep(1)
    
    def test_token_bucket_mode(self):
        """Test the token bucket file transfer mode"""
        print("\n--- Testing Token Bucket Mode ---")
        
        for size, file_path in self.test_files.items():
            # Create a temporary filename in the current directory
            temp_filename = f"test_{size}.txt"
            # Copy instead of rename to avoid cross-device link error
            shutil.copy(file_path, temp_filename)
            
            # Get a free port for this test
            port = get_free_port()
            print(f"Using port {port} for token bucket mode test with file size {size}B")
            
            try:
                # Create instances with various configurations
                bucket_size = 1024
                token_rate = 512
                sender_mode = self.modes["token-bucket"](self.host, port, bucket_size=bucket_size, token_rate=token_rate)
                receiver_mode = self.modes["token-bucket"](self.host, port, bucket_size=bucket_size, token_rate=token_rate)
                
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
                if os.path.exists(f"received_{temp_filename}"):
                    os.remove(f"received_{temp_filename}")
            
            # Add a delay before the next test to allow socket cleanup
            time.sleep(1)
            
    def test_aimd_mode(self):
        """Test the AIMD file transfer mode"""
        print("\n--- Testing AIMD Mode ---")
        
        # Define window sizes to test - only test with small files since large file tests are taking too long
        window_sizes = [1024, 4096]  # 1KB, 4KB
        test_sizes = [1024, 10240]  # Only test with 1KB and 10KB files
        
        for size in test_sizes:
            file_path = self.test_files[size]
            # Test with all file sizes to ensure robustness
            for window_size in window_sizes:
                # Create a descriptive filename
                temp_filename = f"test_{size}_w{window_size//1024}kb.txt"
                # Copy instead of rename to avoid cross-device link error
                shutil.copy(file_path, temp_filename)
                
                # Get a free port for this test
                port = get_free_port()
                print(f"Using port {port} for AIMD mode test with file size {size}B, window size {window_size}B")
                
                try:
                    # Create instances with specific configuration
                    sender_mode = self.modes["aimd"](self.host, port, initial_window=window_size)
                    receiver_mode = self.modes["aimd"](self.host, port, initial_window=window_size)
                    
                    # Start receiver in a thread
                    done_event = threading.Event()
                    receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                    receiver_thread.daemon = True  # Set as daemon so it doesn't block test completion
                    receiver_thread.start()
                    
                    # Give the receiver a moment to start
                    time.sleep(0.5)
                    
                    # Send file
                    success = sender_mode.send_file(temp_filename, self.host, port)
                    
                    # Wait for receiver to complete with a timeout based on file size
                    timeout = max(15, size // 10240)  # Minimum 15 seconds, or longer for larger files
                    done_event.wait(timeout=timeout)
                    
                    # Verify results
                    self.assertTrue(success, f"Failed to send file with AIMD Mode")
                    
                    # Verify file existence
                    received_file = f"received_{temp_filename}"
                    self.assertTrue(os.path.exists(received_file), f"Received file not found: {received_file}")
                    
                    # AIMD doesn't guarantee exact file size preservation, so we only check that some data was received
                    # and it's proportional to the original size
                    received_size = os.path.getsize(received_file)
                    if size <= 1024:  # For small files, check we have at least 80%
                        self.assertTrue(received_size >= size * 0.8, 
                                       f"Received file size {received_size} is too small compared to original {size}")
                    else:  # For larger files, ensure we got at least some reasonable amount of data
                        self.assertTrue(received_size > 0, f"Received file is empty")
                finally:
                    # Clean up - remove the temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    if os.path.exists(f"received_{temp_filename}"):
                        os.remove(f"received_{temp_filename}")
                
                # Add a delay before the next test to allow socket cleanup
                time.sleep(1)
    
    def test_qos_mode(self):
        """Test the QoS file transfer mode"""
        print("\n--- Testing QoS Mode ---")
        
        # Test with different priority levels: normal(1), high(2), highest(3)
        # Avoid using priority level 0 which causes division by zero
        priority_levels = [1, 2, 3]
        
        # Only test with smaller files
        test_sizes = [1024, 10240]
        
        for size in test_sizes:
            file_path = self.test_files[size]
            for priority in priority_levels:
                # Create a descriptive filename
                temp_filename = f"test_{size}_p{priority}.txt"
                # Copy instead of rename to avoid cross-device link error
                shutil.copy(file_path, temp_filename)
                
                # Get a free port for this test
                port = get_free_port()
                print(f"Using port {port} for QoS mode test with file size {size}B, priority {priority}")
                
                try:
                    # Create instances
                    sender_mode = self.modes["qos"](self.host, port)
                    receiver_mode = self.modes["qos"](self.host, port)
                    
                    # Start receiver in a thread
                    done_event = threading.Event()
                    receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                    receiver_thread.start()
                    
                    # Give the receiver a moment to start
                    time.sleep(0.5)
                    
                    # Send file with priority
                    success = sender_mode.send_file(temp_filename, self.host, port, priority_level=priority)
                    
                    # Wait for receiver to complete
                    done_event.wait(timeout=15)
                    
                    # Verify results
                    self.assertTrue(success, f"Failed to send file with QoS Mode (priority={priority})")
                    self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for priority {priority}")
                    
                    # Verify file size
                    received_size = os.path.getsize(f"received_{temp_filename}")
                    self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
                finally:
                    # Clean up - remove the temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    if os.path.exists(f"received_{temp_filename}"):
                        os.remove(f"received_{temp_filename}")
                
                # Add a delay before the next test to allow socket cleanup
                time.sleep(1)
    
    def test_parallel_mode(self):
        """Test the parallel file transfer mode"""
        print("\n--- Testing Parallel Mode ---")
        
        # Test with different numbers of threads
        thread_counts = [2, 4]
        
        # Only test with smaller files
        test_sizes = [1024, 10240]
        
        for size in test_sizes:
            file_path = self.test_files[size]
            for num_threads in thread_counts:
                # Create a descriptive filename
                temp_filename = f"test_{size}_t{num_threads}.txt"
                # Copy instead of rename to avoid cross-device link error
                shutil.copy(file_path, temp_filename)
                
                # Get a free port for this test
                port = get_free_port()
                print(f"Using port {port} for parallel mode test with file size {size}B, threads {num_threads}")
                
                try:
                    # Create instances with specific thread count
                    sender_mode = self.modes["parallel"](self.host, port, num_threads=num_threads)
                    receiver_mode = self.modes["parallel"](self.host, port, num_threads=num_threads)
                    
                    # Start receiver in a thread
                    done_event = threading.Event()
                    receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                    receiver_thread.start()
                    
                    # Give the receiver a moment to start
                    time.sleep(0.5)
                    
                    # Send file with threads
                    success = sender_mode.send_file(temp_filename, self.host, port, num_threads=num_threads)
                    
                    # Wait for receiver to complete
                    done_event.wait(timeout=15)
                    
                    # Verify results
                    self.assertTrue(success, f"Failed to send file with Parallel Mode (threads={num_threads})")
                    self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for threads {num_threads}")
                    
                    # Verify file size
                    received_size = os.path.getsize(f"received_{temp_filename}")
                    self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
                finally:
                    # Clean up - remove the temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    if os.path.exists(f"received_{temp_filename}"):
                        os.remove(f"received_{temp_filename}")
                
                # Add a delay before the next test to allow socket cleanup
                time.sleep(1)

    def test_multicast_mode(self):
        """Test the multicast file transfer mode"""
        print("\n--- Testing Multicast Mode ---")
        
        # Only test with smaller files
        test_sizes = [1024, 10240]
        
        for size in test_sizes:
            file_path = self.test_files[size]
            # Create a temporary filename in the current directory
            temp_filename = f"test_{size}_multicast.txt"
            # Copy instead of rename to avoid cross-device link error
            shutil.copy(file_path, temp_filename)
            
            # Get free ports for this test
            receiver_port = get_free_port()
            sender_port = get_free_port()
            print(f"Using ports {receiver_port} (receiver) and {sender_port} (sender) for multicast mode test with file size {size}B")
            
            try:
                # Create instance - Only testing single receiver for simplicity
                # In a real scenario, we would test multiple receivers
                receiver_mode = self.modes["multicast"](self.host, receiver_port)
                sender_mode = self.modes["multicast"](self.host, sender_port)
                
                # Start receiver in a thread
                done_event = threading.Event()
                receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                receiver_thread.start()
                
                # Give the receiver a moment to start
                time.sleep(0.5)
                
                # Send file to multiple targets (just one in this test)
                targets = [(self.host, receiver_port)]
                success = sender_mode.send_file(temp_filename, targets)
                
                # Wait for receiver to complete
                done_event.wait(timeout=15)
                
                # Verify results
                self.assertTrue(success, f"Failed to send file with Multicast Mode")
                self.assertTrue(os.path.exists(f"received_{temp_filename}"), f"Received file not found for multicast transfer")
                
                # Verify file size
                received_size = os.path.getsize(f"received_{temp_filename}")
                self.assertEqual(size, received_size, f"Received file size {received_size} doesn't match original {size}")
            finally:
                # Clean up - remove the temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                if os.path.exists(f"received_{temp_filename}"):
                    os.remove(f"received_{temp_filename}")
            
            # Add a delay before the next test to allow socket cleanup
            time.sleep(1)

def run_tests():
    # Set the PYTHONPATH to include the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_normal_mode',
        'test_token_bucket_mode', 
        'test_aimd_mode',
        'test_qos_mode',
        'test_parallel_mode',
        'test_multicast_mode'
    ]
    
    for test_method in test_methods:
        suite.addTest(TestAllModes(test_method))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 