"""
Tests for the RemoteLLM class.

This module tests the RemoteLLM implementation to ensure that it correctly
handles API requests, responses, errors, and fallbacks.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os
import sys
from pathlib import Path
import json
import requests
import uuid
import certifi

from plainspeak.core.llm import RemoteLLM


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data, status_code=200, raise_for_status=None):
        self.json_data = json_data
        self.status_code = status_code
        self.raise_for_status = raise_for_status or (lambda: None if status_code < 400 else 
                                              exec('raise requests.HTTPError()'))
        
    def json(self):
        return self.json_data


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
            timeout=1  # Short timeout for faster tests
        )
        
        # Replace logger with mock to avoid cluttering test output
        self.llm.logger = MagicMock()
    
    @patch('requests.post')
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
        self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {self.api_key}")
        self.assertEqual(kwargs['json']['text'], "list files")
    
    @patch('requests.post')
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
    
    @patch('requests.post')
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
    
    @patch('requests.post')
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
    
    @patch('requests.post')
    def test_authentication_error(self, mock_post):
        """Test handling of authentication errors."""
        # Mock 401 response
        response = MockResponse({}, 401)
        
        def raise_http_error():
            raise requests.HTTPError()
            
        response.raise_for_status = raise_http_error
        mock_post.return_value = response
        mock_post.side_effect = [requests.HTTPError(), requests.HTTPError()]
        
        # Call method (should fall back to simple parsing)
        result = self.llm.parse_natural_language("list files")
        
        # Verify result is from fallback method
        self.assertEqual(result["verb"], "list")
        
        # Verify only tried once (no retry for auth errors)
        self.assertEqual(mock_post.call_count, 1)
    
    @patch('requests.post')
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
    
    @patch('requests.post')
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
    
    @patch('requests.post')
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
    
    @patch('requests.post')
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

    @patch('requests.post')
    @patch('certifi.where')
    def test_ssl_certificate_handling(self, mock_certifi_where, mock_post):
        """Test SSL certificate verification handling."""
        # Setup mocks
        expected_cert_path = '/path/to/cert.pem'
        mock_certifi_where.return_value = expected_cert_path
        mock_post.return_value = MockResponse({"verb": "test", "args": {}})
        
        # Test default SSL verification (using certifi)
        llm = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verify_ssl=True
        )
        
        llm.parse_natural_language("test command")
        
        # Verify certifi was used
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['verify'], expected_cert_path)
        
        # Test with SSL verification disabled
        mock_post.reset_mock()
        llm = RemoteLLM(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            verify_ssl=False
        )
        
        llm.parse_natural_language("test command")
        
        # Verify SSL verification was disabled
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['verify'], False)
        
        # Test with custom certificate path
        mock_post.reset_mock()
        custom_cert_path = '/custom/cert.pem'
        
        with patch('os.path.exists', return_value=True):
            llm = RemoteLLM(
                api_endpoint=self.api_endpoint,
                api_key=self.api_key,
                verify_ssl=True,
                ssl_cert_path=custom_cert_path
            )
            
            llm.parse_natural_language("test command")
            
            # Verify custom certificate was used
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['verify'], custom_cert_path)

    @patch('requests.post')
    @patch('uuid.uuid4')
    def test_request_id_tracking(self, mock_uuid4, mock_post):
        """Test request ID tracking for API calls."""
        # Setup mocks
        request_id = "test-uuid-12345"
        mock_uuid4.return_value = Mock(
            __str__=lambda self: request_id
        )
        mock_post.return_value = MockResponse({"verb": "test", "args": {}})
        
        # Make API request
        self.llm.parse_natural_language("test command")
        
        # Verify request ID was tracked
        self.assertIn(request_id, self.llm.request_ids)
        self.assertTrue(self.llm.request_ids[request_id])
        
        # Verify request ID was included in headers
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['X-Request-ID'], request_id)
        
        # Verify request ID was included in payload
        self.assertEqual(kwargs['json']['request_id'], request_id)
        
    @patch('requests.post')
    def test_consecutive_api_calls(self, mock_post):
        """Test multiple consecutive API calls."""
        # Setup mock to return different responses
        mock_post.side_effect = [
            MockResponse({"verb": "list", "args": {"path": "."}}),
            MockResponse({"verb": "find", "args": {"pattern": "*.txt"}}),
            MockResponse({"verb": "grep", "args": {"text": "error", "file": "log.txt"}})
        ]
        
        # Make multiple API calls
        results = [
            self.llm.parse_natural_language("list files"),
            self.llm.parse_natural_language("find text files"),
            self.llm.parse_natural_language("search for errors in log")
        ]
        
        # Verify all calls were made
        self.assertEqual(mock_post.call_count, 3)
        
        # Verify responses were correctly processed
        self.assertEqual(results[0]["verb"], "list")
        self.assertEqual(results[1]["verb"], "find")
        self.assertEqual(results[2]["verb"], "grep")
        
    @patch('requests.post')
    def test_rate_limiting_tracking(self, mock_post):
        """Test tracking for rate limiting."""
        # Setup mock
        mock_post.return_value = MockResponse({"verb": "test", "args": {}})
        
        # Clear the LRU cache first to ensure clean state
        self.llm.parse_natural_language.cache_clear()
        
        # Make multiple API calls with different inputs to avoid cache hits
        initial_count = self.llm.request_count
        
        for i in range(5):
            # Use different input to avoid cache hits
            self.llm.parse_natural_language(f"test command {i}")
        
        # Verify request counter was incremented
        self.assertEqual(self.llm.request_count, initial_count + 5)
        
        # Verify unique request IDs were generated
        self.assertEqual(len(self.llm.request_ids), 5)


if __name__ == "__main__":
    unittest.main() 