#!/usr/bin/env python3
import sys
import unittest
import argparse
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from test_transfer_modes import TestTransferModes

def main():
    parser = argparse.ArgumentParser(description='Test transfer modes in PeerCrypt')
    parser.add_argument('--mode', type=str, choices=['all', 'normal', 'token-bucket', 'aimd', 'qos', 'parallel', 'multicast'],
                        default='all', help='Specify which transfer mode to test')
    
    args = parser.parse_args()
    
    # Create the test suite based on the requested mode
    suite = unittest.TestSuite()
    
    if args.mode == 'all':
        # Add all tests using TestLoader
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestTransferModes)
    elif args.mode == 'normal':
        suite.addTest(TestTransferModes('test_normal_mode'))
    elif args.mode == 'token-bucket':
        suite.addTest(TestTransferModes('test_token_bucket_mode'))
    elif args.mode == 'aimd':
        suite.addTest(TestTransferModes('test_aimd_mode'))
    elif args.mode == 'qos':
        suite.addTest(TestTransferModes('test_qos_mode'))
    elif args.mode == 'parallel':
        suite.addTest(TestTransferModes('test_parallel_mode'))
    elif args.mode == 'multicast':
        suite.addTest(TestTransferModes('test_multicast_mode'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main()) 