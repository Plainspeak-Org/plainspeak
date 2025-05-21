"""Tests for the main CLI function."""

import unittest
from unittest.mock import patch

from plainspeak.cli.main import main


class TestMainFunction(unittest.TestCase):
    """Test suite for the main function."""

    @patch("plainspeak.cli.main.app")
    def test_main_function(self, mock_app):
        """Test that main function calls typer app."""
        # Call the main function
        main()

        # Verify that the app was called
        mock_app.assert_called_once_with()
