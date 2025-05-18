"""
Tests for the RemoteLLM class.

This module tests the RemoteLLM implementation to ensure that it correctly
handles API requests, responses, errors, and fallbacks.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock, ANY
import tempfile
import os
import sys
from pathlib import Path
import json
import requests
import uuid
import certifi
import time

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
        
        # Create RemoteLLM instance with appropriate settings for testing
        self.llm = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            retry_count=2,  # Reduce retries for faster tests
            timeout=1,  # Short timeout for faster tests
            rate_limit_per_minute=10
        )
        
        # Replace logger with mock to avoid cluttering test output
        self.llm.logger = MagicMock()
        
        # Mock time.sleep to speed up tests
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
    
    def tearDown(self):
        """Clean up after each test."""
        self.llm.close()
        self.sleep_patcher.stop()
    
    @patch('requests.Session.post')
    def test_parse_natural_language_success(self, mock_post):
        """Test successful parsing of natural language."""
        # Mock successful API response
        expected_result = {"verb": "list", "args": {"path": "."}}
        mock_post.return_value = MockResponse(expected_result)
        
        # Call method
        result = self.llm.parse_natural_language("list files")
        
        # Verify result
        self.assertEqual(result, expected_result)
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        # Check that the correct API endpoint is called
        self.assertEqual(args[0], f"{self.api_endpoint}/parse")
        self.assertEqual(kwargs['json']['text'], "list files")
    
    @patch('requests.Session.post')
    def test_parse_natural_language_with_locale(self, mock_post):
        """Test parsing with locale information."""
        # Mock successful API response
        expected_result = {"verb": "liste", "args": {"path": "."}}
        mock_post.return_value = MockResponse(expected_result)
        
        # Call method
        result = self.llm.parse_natural_language_with_locale("liste les fichiers", "fr_FR")
        
        # Verify result
        self.assertEqual(result, expected_result)
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['locale'], "fr_FR")
    
    @patch('requests.Session.post')
    def test_api_error_handling(self, mock_post):
        """Test error handling for API failures."""
        # Mock API error
        mock_post.side_effect = requests.RequestException("API connection error")
        
        # Call method (should fall back to simple parsing)
        result = self.llm.parse_natural_language("list files")
        
        # Verify result is from fallback method
        self.assertEqual(result["verb"], "list")
        self.assertIn("path", result["args"])
        
        # Verify retry attempts
        self.assertEqual(mock_post.call_count, self.llm.retry_count)
        
        # Verify error logging
        self.llm.logger.error.assert_called()
    
    @patch('requests.Session.post')
    def test_invalid_api_response(self, mock_post):
        """Test handling of invalid API responses."""
        # Mock invalid response (missing expected fields)
        mock_post.return_value = MockResponse({"some_unexpected_field": "value"})
        
        # Call method (should fall back to simple parsing)
        result = self.llm.parse_natural_language("list files")
        
        # Verify result is from fallback method
        self.assertEqual(result["verb"], "list")
        
        # Verify warning logged
        self.llm.logger.warning.assert_called()
    
    @patch('requests.Session.post')
    def test_invalid_json_response(self, mock_post):
        """Test handling of responses with invalid JSON."""
        # Mock response with invalid JSON
        mock_post.side_effect = ValueError("Invalid JSON response from API")
        
        # Call method (should fall back to simple parsing)
        result = self.llm.parse_natural_language("list files")
        
        # Verify result is from fallback method
        self.assertEqual(result["verb"], "list")
        
        # Verify logging
        self.llm.logger.warning.assert_any_call(ANY)
    
    @patch('requests.Session.post')
    def test_authentication_error(self, mock_post):
        """Test handling of authentication errors."""
        # Mock HTTP error response
        mock_response = MockResponse({}, 401)
        
        # Configure the mock to raise the error when raise_for_status is called
        mock_post.return_value = mock_response
        
        # Call method (should fall back to simple parsing)
        result = self.llm.parse_natural_language("list files")
        
        # Verify result is from fallback method
        self.assertEqual(result["verb"], "list")
        
        # Verify only tried once (no retry for auth errors)
        self.assertEqual(mock_post.call_count, 1)
    
    @patch('requests.Session.post')
    def test_get_improved_command(self, mock_post):
        """Test getting improved commands based on feedback."""
        # Mock successful API response
        expected_command = "find . -name '*.txt'"
        mock_post.return_value = MockResponse({"command": expected_command})
        
        # Call method
        feedback_data = {"positive": False}
        previous_commands = ["find . -type f"]
        result = self.llm.get_improved_command("find text files", feedback_data, previous_commands)
        
        # Verify result
        self.assertEqual(result, expected_command)
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['query'], "find text files")
        self.assertEqual(kwargs['json']['feedback_data'], feedback_data)
        self.assertEqual(kwargs['json']['previous_commands'], previous_commands)
    
    @patch('requests.Session.post')
    def test_get_improved_command_fallback(self, mock_post):
        """Test fallback for improved command when API fails."""
        # Mock API error
        mock_post.side_effect = requests.RequestException("API connection error")
        
        # Call method with a corrected command in feedback
        feedback_data = {"corrected_command": "ls -la"}
        previous_commands = ["ls"]
        result = self.llm.get_improved_command("list files", feedback_data, previous_commands)
        
        # Verify result falls back to corrected_command
        self.assertEqual(result, "ls -la")
        
        # Try again with no corrected command but with previous commands
        feedback_data = {"positive": False}
        previous_commands = ["find . -type f"]
        result = self.llm.get_improved_command("find files", feedback_data, previous_commands)
        
        # Verify result falls back to last previous command
        self.assertEqual(result, "find . -type f")
        
        # Try again with no feedback or previous commands
        result = self.llm.get_improved_command("list files", {}, [])
        
        # Verify result falls back to empty string
        self.assertEqual(result, "")
    
    @patch('requests.Session.post')
    def test_suggest_verbs(self, mock_post):
        """Test suggesting verbs based on partial input."""
        # Mock successful API response
        expected_verbs = ["list", "locate", "lookup"]
        mock_post.return_value = MockResponse({"verbs": expected_verbs})
        
        # Call method
        result = self.llm.suggest_verbs("l")
        
        # Verify result
        self.assertEqual(result, expected_verbs)
        
        # Verify API call
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_suggest_verbs_fallback(self, mock_post):
        """Test fallback for verb suggestions when API fails."""
        # Mock API error
        mock_post.side_effect = requests.RequestException("API connection error")
        
        # Call method
        result = self.llm.suggest_verbs("l")
        
        # Verify result contains default verbs starting with "l"
        self.assertIn("list", result)
        for verb in result:
            self.assertTrue(verb.startswith("l"))
        
        # Call with empty string
        result = self.llm.suggest_verbs("")
        
        # Verify result contains all default verbs
        self.assertIn("list", result)
        self.assertIn("find", result)
        self.assertIn("search", result)
    
    def test_empty_input(self):
        """Test handling of empty input strings."""
        result = self.llm.parse_natural_language("")
        self.assertEqual(result, {"verb": None, "args": {}})
        
        result = self.llm.parse_natural_language_with_locale("", "en_US")
        self.assertEqual(result, {"verb": None, "args": {}})

    @patch('requests.Session.post')
    @patch('certifi.where')
    def test_ssl_certificate_handling(self, mock_certifi_where, mock_post):
        """Test SSL certificate verification handling."""
        # Setup mocks
        expected_cert_path = '/path/to/cert.pem'
        mock_certifi_where.return_value = expected_cert_path
        mock_post.return_value = MockResponse({"verb": "test", "args": {}})
        
        # Create LLM instances with different SSL settings
        llm_verify_ssl = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verify_ssl=True
        )
        llm_verify_ssl.logger = MagicMock()
        
        # Call parse method
        llm_verify_ssl.parse_natural_language("test")
        
        # Verify SSL certificate is set correctly
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['verify'], expected_cert_path)
        
        # Create LLM with custom certificate
        with tempfile.NamedTemporaryFile() as temp_cert:
            temp_cert_path = temp_cert.name
            llm_custom_cert = RemoteLLM(
                api_endpoint=self.api_endpoint,
                api_key=self.api_key,
                verify_ssl=True,
                ssl_cert_path=temp_cert_path
            )
            llm_custom_cert.logger = MagicMock()
            
            # Call parse method
            llm_custom_cert.parse_natural_language("test")
            
            # Verify custom certificate is used
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['verify'], temp_cert_path)
        
        # Create LLM with SSL verification disabled
        llm_no_verify = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verify_ssl=False
        )
        llm_no_verify.logger = MagicMock()
        
        # Call parse method
        llm_no_verify.parse_natural_language("test")
        
        # Verify SSL verification is disabled
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['verify'], False)
        
        # Clean up
        llm_verify_ssl.close()
        llm_custom_cert.close()
        llm_no_verify.close()

    @patch('requests.Session.post')
    @patch('uuid.uuid4')
    def test_request_id_tracking(self, mock_uuid4, mock_post):
        """Test that request IDs are properly tracked."""
        # Setup mocks
        test_uuid = "12345678-1234-5678-1234-567812345678"
        mock_uuid4.return_value = test_uuid
        mock_post.return_value = MockResponse({"verb": "test", "args": {}})
        
        # Call method
        self.llm.parse_natural_language("test request")
        
        # Verify request ID is in headers and payload
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['X-Request-ID'], test_uuid)
        self.assertEqual(kwargs['json']['request_id'], test_uuid)
        
        # Verify request ID is tracked in the instance
        self.assertTrue(test_uuid in self.llm.request_ids)

    @patch('requests.Session.post')
    def test_consecutive_api_calls(self, mock_post):
        """Test that multiple consecutive API calls work properly."""
        # Setup mock for multiple responses
        responses = [
            MockResponse({"verb": "first", "args": {}}),
            MockResponse({"verb": "second", "args": {}}),
            MockResponse({"verb": "third", "args": {}})
        ]
        mock_post.side_effect = responses
        
        # Make multiple calls
        result1 = self.llm.parse_natural_language("first call")
        result2 = self.llm.parse_natural_language("second call")
        result3 = self.llm.parse_natural_language("third call")
        
        # Verify results
        self.assertEqual(result1["verb"], "first")
        self.assertEqual(result2["verb"], "second")
        self.assertEqual(result3["verb"], "third")
        
        # Verify multiple calls were made
        self.assertEqual(mock_post.call_count, 3)

    @patch('requests.Session.post')
    def test_rate_limiting_tracking(self, mock_post):
        """Test the rate limiting functionality."""
        # Mock response
        mock_post.return_value = MockResponse({"verb": "test", "args": {}})
        
        # Set a very low rate limit for testing
        self.llm.rate_limit_per_minute = 2
        
        # Make multiple calls
        result1 = self.llm.parse_natural_language("first call")
        result2 = self.llm.parse_natural_language("second call")
        
        # Third call should trigger rate limit
        with self.assertRaises(RuntimeError) as context:
            self.llm._make_api_request("test", {})
            
        self.assertTrue("Rate limit exceeded" in str(context.exception))
        
        # Check that warning was logged
        self.llm.logger.warning.assert_any_call(
            ANY  # Use ANY since we don't need to check the exact message
        )
        # At least one warning should contain "Rate limit exceeded"
        warning_calls = [call_args[0][0] for call_args in self.llm.logger.warning.call_args_list]
        rate_limit_warnings = [call for call in warning_calls if "Rate limit exceeded" in call]
        self.assertTrue(len(rate_limit_warnings) > 0, "Expected a warning about rate limit being exceeded")
    
    @patch('requests.Session.post')
    def test_backoff_retry_logic(self, mock_post):
        """Test that backoff retry logic works correctly."""
        # First call fails, second succeeds
        mock_post.side_effect = [
            requests.ConnectionError("Connection error"),
            MockResponse({"verb": "test", "args": {}})
        ]
        
        # Set backoff factor
        self.llm.backoff_factor = 0.1
        
        # Call method
        result = self.llm.parse_natural_language("test backoff")
        
        # Verify result
        self.assertEqual(result["verb"], "test")
        
        # Verify sleep was called for backoff
        self.mock_sleep.assert_called()
        
        # We don't care about the exact sleep duration, just that it was called
        self.assertTrue(len(self.mock_sleep.call_args_list) > 0, 
                       "Expected sleep to be called for backoff")
    
    @patch('requests.Session.post')
    def test_circuit_breaker(self, mock_post):
        """Test the circuit breaker functionality."""
        # Set up to consistently fail
        mock_post.side_effect = requests.ConnectionError("Connection error")
        
        # Make calls to trip the circuit breaker (need 5 consecutive failures)
        for _ in range(5):
            try:
                self.llm._make_api_request("test", {})
            except:
                pass
        
        # Verify circuit breaker is open
        self.assertTrue(self.llm.circuit_open)
        
        # Next call should immediately raise a circuit breaker exception
        with self.assertRaises(RuntimeError) as context:
            self.llm._make_api_request("test", {})
            
        self.assertTrue("Circuit breaker open" in str(context.exception))

    @patch('requests.Session.post')
    def test_retry_after_rate_limiting(self, mock_post):
        """Test handling of 429 rate limiting responses with Retry-After header."""
        # Create a mock response with 429 status
        rate_limit_response = MockResponse(
            {"error": "rate limit exceeded"},
            status_code=429,
            headers={"Retry-After": "2"}
        )
        
        # Configure mock to raise HTTPError with our response when raise_for_status is called
        def raise_http_error():
            raise requests.HTTPError("Rate limited", response=rate_limit_response)
        
        err_response = MockResponse({}, 429, raise_for_status=raise_http_error, headers={"Retry-After": "2"})
        
        # Configure mock_post with a side effect
        mock_post.side_effect = [
            err_response,  # First call gets a 429
            MockResponse({"verb": "test", "args": {}})  # Second call succeeds
        ]
        
        # Call parse method
        result = self.llm.parse_natural_language("test rate limit")
        
        # Verify that we get a result from the second call
        self.assertEqual(result["verb"], "test")
        
        # Verify that sleep was called
        self.mock_sleep.assert_called()

    @patch('requests.Session.post')
    def test_api_key_rotation(self, mock_post):
        """Test API key rotation on authentication errors."""
        # Create LLM with key rotation enabled
        llm_with_rotation = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key="original-key",
            rotate_keys=True,
            api_keys=["original-key", "backup-key-1", "backup-key-2"],
            retry_count=1  # Only retry once for testing
        )
        llm_with_rotation.logger = MagicMock()
        llm_with_rotation.session = MagicMock()
        
        # First call gets auth error, second succeeds with rotated key
        llm_with_rotation.session.post.side_effect = [
            requests.HTTPError("Unauthorized", response=MockResponse({}, 401)),
            MockResponse({"verb": "test", "args": {}})
        ]
        
        # Call method
        result = llm_with_rotation.parse_natural_language("test key rotation")
        
        # Verify key was rotated
        self.assertEqual(llm_with_rotation.api_key, "backup-key-1")
        self.assertEqual(llm_with_rotation.current_key_index, 1)
        
        # Verify result
        self.assertEqual(result["verb"], "test")
        
        # Clean up
        llm_with_rotation.close()
        
    @patch('requests.Session.post')
    def test_all_keys_failing(self, mock_post):
        """Test handling when all API keys fail."""
        # Create LLM with key rotation enabled but only one key
        llm_limited_keys = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key="only-key",
            rotate_keys=True,
            retry_count=1  # Only retry once for testing
        )
        llm_limited_keys.logger = MagicMock()
        
        # Mock authentication error for the only key
        mock_post.side_effect = requests.HTTPError(
            "Unauthorized", 
            response=MockResponse({}, 401)
        )
        
        # Call method (should fall back to simple parsing)
        result = llm_limited_keys.parse_natural_language("test all keys failing")
        
        # Verify result is from fallback
        self.assertEqual(result["verb"], "test")
        
        # Clean up
        llm_limited_keys.close()


if __name__ == "__main__":
    unittest.main() 