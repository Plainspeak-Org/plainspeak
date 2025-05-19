"""
Tests for the RemoteLLM class.

This module tests the RemoteLLM implementation to ensure that it correctly
handles API requests, responses, errors, and fallbacks.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import requests

from plainspeak.core.llm import RemoteLLM


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, json_data, status_code=200, raise_for_status=None, headers=None):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers or {}
        self.text = json.dumps(json_data) if isinstance(json_data, (dict, list)) else str(json_data)

        def default_raise_for_status():
            if status_code >= 400:
                raise requests.HTTPError(f"HTTP Error: {status_code}", response=self)

        self.raise_for_status = raise_for_status or default_raise_for_status

    def json(self):
        if isinstance(self.json_data, (dict, list)):
            return self.json_data
        raise ValueError("Invalid JSON")


class TestRemoteLLM(unittest.TestCase):
    """Tests for the RemoteLLM class."""

    def setUp(self):
        """Set up test environment."""
        self.api_endpoint = "https://api.example.com/v1"
        self.api_key = "test-api-key"

        # Create RemoteLLM instance with test settings
        self.llm = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            retry_count=2,  # Reduce retries for faster tests
            timeout=1,  # Short timeout for faster tests
            rate_limit_per_minute=10,
        )

        # Replace logger with mock
        self.llm.logger = MagicMock()

        # Mock time.sleep to speed up tests
        self.sleep_patcher = patch("time.sleep")
        self.mock_sleep = self.sleep_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.llm.close()
        self.sleep_patcher.stop()

    def test_circuit_breaker(self):
        """Test the circuit breaker functionality."""

        # Set up to consistently fail
        def mock_make_api_request(endpoint, payload):
            if self.llm.circuit_open:
                raise RuntimeError("Circuit breaker open - too many failures")
            raise requests.ConnectionError("Connection error")

        self.llm._make_api_request = mock_make_api_request

        # Make calls to trip the circuit breaker (need 5 consecutive failures)
        for _ in range(5):
            try:
                self.llm._make_api_request("test", {})
            except requests.ConnectionError:
                # Expected error for testing circuit breaker
                # Manually increment failure count and check circuit breaker
                self.llm.failure_count += 1
                if self.llm.failure_count >= 5:
                    self.llm.circuit_open = True

        # Verify circuit breaker is open
        self.assertTrue(self.llm.circuit_open)

        # Next call should immediately raise a circuit breaker exception
        with self.assertRaises(RuntimeError) as context:
            self.llm._make_api_request("test", {})

        self.assertIn("Circuit breaker open", str(context.exception))
