#!/usr/bin/env python3
"""
Test cross-platform fallbacks for health_check.py memory and load checks.

Simulates missing /proc files (non-Linux environment) and verifies
that the fallback paths return meaningful results instead of generic
failure messages.
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.health_check import check_memory_usage, check_load_average


class TestHealthCheckFallback(unittest.TestCase):
    """Test that memory and load checks degrade gracefully without /proc."""

    @patch("os.path.exists")
    def test_memory_fallback_no_proc(self, mock_exists):
        """Returns gracefully when /proc/meminfo is absent and no macOS tools."""
        def exists_side_effect(path):
            if path in ("/proc/meminfo", "/usr/bin/vm_stat"):
                return False
            return True
        mock_exists.side_effect = exists_side_effect
        status, detail, pct = check_memory_usage()
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertIsInstance(pct, (int, float))

    @patch("os.path.exists")
    def test_load_fallback_no_proc(self, mock_exists):
        """Uses os.getloadavg() when /proc/loadavg is absent."""
        mock_exists.return_value = False
        try:
            status, detail, load = check_load_average()
            self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
            self.assertIsInstance(load, float)
        except NotImplementedError:
            self.skipTest("os.getloadavg() not available")

    def test_memory_returns_tuple(self):
        """Always returns a 3-tuple."""
        result = check_memory_usage()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_load_returns_tuple(self):
        """Always returns a 3-tuple."""
        result = check_load_average()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_memory_detail_contains_pct(self):
        """Detail message contains a percentage."""
        status, detail, pct = check_memory_usage()
        self.assertIn("%", detail)


if __name__ == "__main__":
    unittest.main()
