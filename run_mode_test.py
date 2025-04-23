#!/usr/bin/env python3
import sys
import unittest
from test_all_modes import TestAllModes

def run_mode_test(mode):
    """Run tests for a specific transfer mode"""
    valid_modes = {
        'normal': 'test_normal_mode',
        'token-bucket': 'test_token_bucket_mode',
        'aimd': 'test_aimd_mode',
        'qos': 'test_qos_mode',
        'parallel': 'test_parallel_mode',
        'multicast': 'test_multicast_mode',
        'all': 'all'
    }
    
    if mode not in valid_modes:
        print(f"Error: Invalid mode '{mode}'")
        print(f"Valid modes: {', '.join(valid_modes.keys())}")
        return 1
    
    # Create test suite
    suite = unittest.TestSuite()
    
    if mode == 'all':
        # Add all tests
        for test_method in valid_modes.values():
            if test_method != 'all':
                suite.addTest(TestAllModes(test_method))
    else:
        # Add specific test
        suite.addTest(TestAllModes(valid_modes[mode]))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_mode_test.py <mode>")
        print("Available modes: normal, token-bucket, aimd, qos, parallel, multicast, all")
        sys.exit(1)
    
    mode = sys.argv[1]
    sys.exit(run_mode_test(mode)) 