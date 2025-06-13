import unittest
import sys
from unittest.mock import patch

# Add project root to sys.path to allow importing config from the parent directory
# This assumes the test script might be run from the 'tests' directory directly.
# If using a test runner from the project root, this might not be needed or could be different.
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import parse_arguments

class TestConfig(unittest.TestCase):

    def test_default_values(self):
        """Test that default values are correctly assigned for new arguments."""
        with patch('sys.argv', ['main.py']):
            args = parse_arguments()
            self.assertIsNotNone(args) # Ensure parsing succeeded
            self.assertEqual(args.rotation_speed, 0.1)
            self.assertEqual(args.depth_effect_strength, 0.5)

    def test_valid_custom_values(self):
        """Test parsing of valid custom values for new arguments."""
        test_argv = [
            'main.py',
            '--rotation_speed', '0.25',
            '--depth_effect_strength', '0.75'
        ]
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNotNone(args) # Ensure parsing succeeded
            self.assertEqual(args.rotation_speed, 0.25)
            self.assertEqual(args.depth_effect_strength, 0.75)

    @patch('sys.stderr') # Suppress print output during this test
    def test_invalid_depth_strength_too_low(self, mock_stderr):
        """Test that depth_effect_strength < 0.0 returns None."""
        test_argv = ['main.py', '--depth_effect_strength', '-0.1']
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNone(args)

    @patch('sys.stderr') # Suppress print output during this test
    def test_invalid_depth_strength_too_high(self, mock_stderr):
        """Test that depth_effect_strength > 1.0 returns None."""
        test_argv = ['main.py', '--depth_effect_strength', '1.1']
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNone(args)

    @patch('sys.stderr') # Suppress print output during this test
    def test_valid_depth_strength_edge_cases(self, mock_stderr):
        """Test edge cases for depth_effect_strength (0.0 and 1.0)."""
        test_argv_low = ['main.py', '--depth_effect_strength', '0.0']
        with patch('sys.argv', test_argv_low):
            args = parse_arguments()
            self.assertIsNotNone(args)
            self.assertEqual(args.depth_effect_strength, 0.0)

        test_argv_high = ['main.py', '--depth_effect_strength', '1.0']
        with patch('sys.argv', test_argv_high):
            args = parse_arguments()
            self.assertIsNotNone(args)
            self.assertEqual(args.depth_effect_strength, 1.0)


if __name__ == '__main__':
    unittest.main()
