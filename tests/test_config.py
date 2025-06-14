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
            self.assertEqual(args.cylindrical_radius_factor, 1.0) # New default check

    def test_valid_custom_values(self):
        """Test parsing of valid custom values for new arguments."""
        test_argv = [
            'main.py',
            '--rotation_speed', '0.25',
            '--depth_effect_strength', '0.75'
        ]
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNotNone(args)
            self.assertEqual(args.rotation_speed, 0.25)
            self.assertEqual(args.depth_effect_strength, 0.75)

    @patch('sys.stderr')
    def test_invalid_depth_strength_too_low(self, mock_stderr):
        """Test that depth_effect_strength < 0.0 returns None."""
        test_argv = ['main.py', '--depth_effect_strength', '-0.1']
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNone(args)

    @patch('sys.stderr')
    def test_invalid_depth_strength_too_high(self, mock_stderr):
        """Test that depth_effect_strength > 1.0 returns None."""
        test_argv = ['main.py', '--depth_effect_strength', '1.1']
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNone(args)

    @patch('sys.stderr')
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

    # Tests for cylindrical_radius_factor
    def test_valid_custom_cylindrical_radius_factor(self):
        """Test parsing of valid custom values for cylindrical_radius_factor."""
        test_argv_small = ['main.py', '--cylindrical_radius_factor', '0.5']
        with patch('sys.argv', test_argv_small):
            args = parse_arguments()
            self.assertIsNotNone(args)
            self.assertEqual(args.cylindrical_radius_factor, 0.5)

        test_argv_large = ['main.py', '--cylindrical_radius_factor', '2.0']
        with patch('sys.argv', test_argv_large):
            args = parse_arguments()
            self.assertIsNotNone(args)
            self.assertEqual(args.cylindrical_radius_factor, 2.0)

    @patch('sys.stderr')
    def test_invalid_cylindrical_radius_factor_zero(self, mock_stderr):
        """Test that cylindrical_radius_factor == 0 returns None."""
        test_argv = ['main.py', '--cylindrical_radius_factor', '0']
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNone(args)

    @patch('sys.stderr')
    def test_invalid_cylindrical_radius_factor_negative(self, mock_stderr):
        """Test that cylindrical_radius_factor < 0 returns None."""
        test_argv = ['main.py', '--cylindrical_radius_factor', '-1.0']
        with patch('sys.argv', test_argv):
            args = parse_arguments()
            self.assertIsNone(args)

if __name__ == '__main__':
    unittest.main()
