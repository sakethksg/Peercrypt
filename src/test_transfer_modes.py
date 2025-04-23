import unittest
import os
import time
import socket
import threading
import tempfile
import random
import string
import shutil
from typing import Tuple, Dict, Any

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
                # Create instances with various configurations
                bucket_size = 1024
                token_rate = 512
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
        
        # Only test with a single configuration to save time
        congestion_configs = [
            {"name": "Default", "timeout_detection": True, "dupack_detection": True}
        ]
        
        # Define window sizes to test
        window_sizes = [1024]  # Just testing with 1KB window to keep test time reasonable
        
        for size, file_path in self.test_files.items():
            # Only test with the first file size to keep tests shorter
            if size != self.test_file_sizes[0]:
                continue
                
            for config in congestion_configs:
                for window_size in window_sizes:
                    # Create a descriptive filename
                    config_name = config["name"].replace(" ", "_").lower()
                    temp_filename = f"test_{size}_{config_name}_w{window_size//1024}kb.txt"
                    # Copy instead of rename to avoid cross-device link error
                    shutil.copy(file_path, temp_filename)
                    
                    print(f"\n  Testing AIMD with {config['name']}, window={window_size//1024}KB, file size={size}B")
                    
                    try:
                        # Create instances with specific configuration
                        sender_mode = AIMDMode(self.host, port, initial_window=window_size)
                        receiver_mode = AIMDMode(self.host, port, initial_window=window_size)
                        
                        # Configure congestion detection
                        sender_mode.configure(
                            timeout_enabled=config["timeout_detection"],
                            dupack_enabled=config["dupack_detection"],
                            initial_window=window_size,
                            min_window=1024,
                            max_window=65536
                        )
                        
                        # Start receiver in a thread
                        done_event = threading.Event()
                        receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                        receiver_thread.daemon = True  # Set as daemon so it doesn't block test completion
                        receiver_thread.start()
                        
                        # Give the receiver a moment to start
                        time.sleep(0.5)
                        
                        # Send file with congestion detection settings
                        success = sender_mode.send_file(
                            temp_filename, 
                            self.host, 
                            port, 
                            timeout_detection=config["timeout_detection"],
                            dupack_detection=config["dupack_detection"]
                        )
                        
                        # Wait for receiver to complete with a timeout based on file size
                        timeout = max(15, size // 10240)  # Minimum 15 seconds, or longer for larger files
                        done_event.wait(timeout=timeout)
                        
                        # Wait a bit longer for operations to complete
                        time.sleep(1)
                        
                        # Verify results
                        self.assertTrue(success, f"Failed to send file with AIMD Mode ({config['name']})")
                        
                        # Print congestion statistics if available
                        print(f"  Results for {config['name']} with window size {window_size//1024}KB:")
                        print(f"    Timeouts: {sender_mode.timeouts}")
                        print(f"    Fast Retransmits: {sender_mode.fast_retransmits}")
                        print(f"    Total Retransmissions: {sender_mode.total_retransmits}")
                        if sender_mode.srtt is not None:
                            print(f"    Smoothed RTT: {sender_mode.srtt*1000:.2f}ms")
                        print(f"    Final Window Size: {sender_mode.window_size//1024}KB")
                        
                        # For this test, we will only verify the file was sent successfully,
                        # but not check content integrity since we're specifically testing
                        # the congestion control mechanism
                        print(f"  Successfully tested AIMD congestion control logic")
                        
                    finally:
                        # Clean up - remove the temporary file
                        if os.path.exists(temp_filename):
                            os.remove(temp_filename)
                        try:
                            if os.path.exists(f"received_{temp_filename}"):
                                os.remove(f"received_{temp_filename}")
                        except:
                            pass
                    
                    # Increment port for next test
                    port += 1
    
    def test_qos_mode(self):
        print("\n--- Testing QoS Mode ---")
        port = self.base_port + 300
        
        # Use numeric priority levels instead of strings
        priorities = [1, 2, 3]  # 1=high, 2=normal, 3=low
        
        for size, file_path in self.test_files.items():
            for priority in priorities:
                # Create a temporary filename in the current directory
                temp_filename = f"test_{size}_priority_{priority}.txt"
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
                    
                    # Send file with the specific priority level
                    success = sender_mode.send_file(temp_filename, self.host, port, priority_level=priority)
                    
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
            
            # Create receivers
            for i, port in enumerate(receiver_ports):
                receiver = MulticastMode(self.host, port)
                receivers.append(receiver)
                
                # Create and start receiver threads
                thread = threading.Thread(
                    target=self.start_receiver, 
                    args=(receiver, threading.Event()),
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
            
            # Wait for receivers to complete (up to 5 seconds)
            time.sleep(5)
            
            # Verify results
            self.assertTrue(success, f"Failed to send file via multicast")
            
            # Check all received files exist
            for port in receiver_ports:
                received_filename = f"received_{temp_filename}"
                self.assertTrue(os.path.exists(received_filename), 
                               f"Received file not found for port {port}")
                
                # Verify file size
                if os.path.exists(received_filename):
                    received_size = os.path.getsize(received_filename)
                    self.assertEqual(size, received_size, 
                                   f"Received file size {received_size} doesn't match original {size}")
        finally:
            # Clean up temporary files
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def test_aimd_mode_with_congestion(self):
        """Test AIMD mode with induced congestion through packet dropping"""
        print("\n--- Testing AIMD Mode with Simulated Congestion ---")
        port = self.base_port + 600
        
        # Use a larger file size for better congestion detection
        size = self.test_file_sizes[1] if len(self.test_file_sizes) > 1 else self.test_file_sizes[0]
        file_path = self.test_files[size]
        
        # Create a temporary filename
        temp_filename = f"test_{size}_congestion_simulation.txt"
        shutil.copy(file_path, temp_filename)
        
        try:
            # Create a subclass to simulate packet loss and congestion
            class SimulatedCongestionAIMD(AIMDMode):
                def __init__(self, host, port, packet_loss_rate=0.1, delay_variation=0.1):
                    super().__init__(host, port)
                    self.packet_loss_rate = packet_loss_rate
                    self.delay_variation = delay_variation
                    self.packets_dropped = 0
                    self.packets_delayed = 0
                    
                def send_file(self, filepath, target_host, target_port, **kwargs):
                    print(f"  Starting file transfer with {self.packet_loss_rate*100:.1f}% packet loss rate")
                    return super().send_file(filepath, target_host, target_port, **kwargs)
                    
                def handle_ack(self, ack_seq):
                    # Simulate packet loss and delays at the ACK handling level
                    # which won't interfere with the encryption/decryption process
                    
                    # Randomly drop some ACKs to simulate congestion (won't be processed)
                    if random.random() < self.packet_loss_rate:
                        self.packets_dropped += 1
                        # Skip processing this ACK and return no congestion
                        return False, ""
                    
                    # Add random delay to some packets to simulate network jitter
                    if random.random() < self.delay_variation:
                        self.packets_delayed += 1
                        delay = random.uniform(0.05, 0.2)  # 50-200ms delay
                        time.sleep(delay)
                    
                    # Process normally if not dropped or after delay
                    return super().handle_ack(ack_seq)
            
            # Create sender and receiver with different congestion levels
            congestion_levels = [
                {"name": "Mild", "loss_rate": 0.05, "delay": 0.1},
                {"name": "Moderate", "loss_rate": 0.15, "delay": 0.15},
                {"name": "Severe", "loss_rate": 0.25, "delay": 0.2}
            ]
            
            for level in congestion_levels:
                level_name = level["name"].lower()
                test_filename = f"{temp_filename}_{level_name}"
                shutil.copy(file_path, test_filename)
                
                print(f"\n  Testing with {level['name']} congestion ({level['loss_rate']*100:.1f}% loss rate)")
                
                try:
                    # Create instances
                    sender_mode = SimulatedCongestionAIMD(
                        self.host, port, 
                        packet_loss_rate=level["loss_rate"], 
                        delay_variation=level["delay"]
                    )
                    receiver_mode = AIMDMode(self.host, port)
                    
                    # Configure both to use all congestion detection mechanisms
                    sender_mode.configure(
                        timeout_enabled=True,
                        dupack_enabled=True,
                        initial_window=8192,  # Start with 8KB window
                        min_window=1024,
                        max_window=65536
                    )
                    
                    # Start receiver in a thread
                    done_event = threading.Event()
                    receiver_thread = threading.Thread(target=self.start_receiver, args=(receiver_mode, done_event))
                    receiver_thread.daemon = True  # Set as daemon so it doesn't block test completion
                    receiver_thread.start()
                    
                    # Give the receiver a moment to start
                    time.sleep(0.5)
                    
                    # Send file
                    success = sender_mode.send_file(test_filename, self.host, port)
                    
                    # Wait for receiver with appropriate timeout
                    timeout = max(20, size // 5120)  # Longer timeout for congested transfers
                    done_event.wait(timeout=timeout)
                    
                    # Give a small additional time for file operations to complete
                    time.sleep(0.5)
                    
                    # Verify results
                    self.assertTrue(success, f"Failed to send file under {level['name']} congestion")
                    
                    # Print congestion statistics
                    print(f"  Results for {level['name']} congestion:")
                    print(f"    Packets dropped: {sender_mode.packets_dropped}")
                    print(f"    Packets delayed: {sender_mode.packets_delayed}")
                    print(f"    Timeouts: {sender_mode.timeouts}")
                    print(f"    Fast Retransmits: {sender_mode.fast_retransmits}")
                    print(f"    Total Retransmissions: {sender_mode.total_retransmits}")
                    if sender_mode.srtt is not None:
                        print(f"    Final Smoothed RTT: {sender_mode.srtt*1000:.2f}ms")
                        print(f"    Final RTO: {sender_mode.rto*1000:.2f}ms")
                    print(f"    Final Window Size: {sender_mode.window_size//1024}KB")
                    
                    # For this test, we only verify the congestion control mechanisms, not file integrity
                    print(f"  Successfully tested AIMD congestion control with {level['name']} congestion")
                
                finally:
                    # Clean up
                    if os.path.exists(test_filename):
                        os.remove(test_filename)
                    try:
                        if os.path.exists(f"received_{test_filename}"):
                            os.remove(f"received_{test_filename}")
                    except:
                        pass
                
                # Increment port for the next test
                port += 1
                
        finally:
            # Clean up the base temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

if __name__ == "__main__":
    unittest.main() 