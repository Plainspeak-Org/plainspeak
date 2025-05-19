"""Test LLM interface functionality."""

from unittest.mock import MagicMock, patch

import pytest

from plainspeak.core.llm import LLMInterface, LLMResponseError, LocalLLMInterface, RemoteLLMInterface


class TestLLMInterface:
    """Test LLM interface functionality."""

    def test_parse_llm_response_empty(self):
        """Test handling of empty LLM response."""
        interface = LLMInterface()
        with pytest.raises(LLMResponseError):
            interface._parse_llm_response("", "test command")

    def test_parse_llm_response_raw_json(self):
        """Test parsing raw JSON response."""
        interface = LLMInterface()
        json_str = '{"verb": "test", "args": {"arg1": "value1"}}'
        result = interface._parse_llm_response(json_str, "test command")
        assert result == {"verb": "test", "args": {"arg1": "value1"}}

    def test_parse_llm_response_markdown_json(self):
        """Test parsing JSON inside markdown code blocks."""
        interface = LLMInterface()
        markdown_json = """Here's the parsed command:
```json
{
    "verb": "test",
    "args": {"arg1": "value1"}
}
```
"""
        result = interface._parse_llm_response(markdown_json, "test command")
        assert result == {"verb": "test", "args": {"arg1": "value1"}}

    def test_parse_llm_response_invalid_json(self):
        """Test handling of invalid JSON response."""
        interface = LLMInterface()
        with pytest.raises(LLMResponseError):
            interface._parse_llm_response("not json", "test command")


class TestRemoteLLMInterface:
    """Test remote LLM interface functionality."""

    def test_remote_llm_api_key_from_config(self):
        """Test API key loading from config."""
        config = MagicMock()
        config.llm.api_key = "test_key"
        interface = RemoteLLMInterface(config)
        assert interface.api_key == "test_key"

    def test_remote_llm_api_key_from_env(self):
        """Test API key loading from environment."""
        config = MagicMock()
        config.llm.api_key = None
        config.llm.api_key_env_var = "TEST_API_KEY"

        with patch.dict("os.environ", {"TEST_API_KEY": "env_key"}):
            interface = RemoteLLMInterface(config)
            assert interface.api_key == "env_key"

    def test_remote_llm_missing_api_key(self):
        """Test error when API key is missing."""
        config = MagicMock()
        config.llm.api_key = None
        config.llm.api_key_env_var = "MISSING_KEY"

        with pytest.raises(ValueError):
            RemoteLLMInterface(config)

    def test_remote_llm_circuit_breaker(self):
        """Test circuit breaker functionality."""
        config = MagicMock()
        config.llm.api_key = "test_key"
        config.llm.circuit_failure_threshold = 2  # Trip after 2 failures
        config.llm.model_name = "test_model"
        config.llm.max_tokens = 100
        config.llm.temperature = 0.7

        # Create a mock OpenAI client that always fails
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Test failure")

        interface = RemoteLLMInterface(config)
        interface.remote_llm = mock_client

        # Reset circuit breaker state
        interface.failure_count = 0
        interface.circuit_tripped = False

        # First call should raise LLMResponseError but not trip circuit
        with pytest.raises(LLMResponseError):
            interface.generate("test prompt")
        assert interface.failure_count == 1
        assert not interface.circuit_tripped

        # Second call should trip the circuit breaker
        with pytest.raises(LLMResponseError):
            interface.generate("test prompt")
        assert interface.failure_count == 2
        assert interface.circuit_tripped  # Circuit should be tripped now

        # Third call should raise RuntimeError due to tripped circuit
        with pytest.raises(RuntimeError, match="Circuit breaker tripped"):
            interface.generate("test prompt")


class TestLocalLLMInterface:
    """Test local LLM interface functionality."""

    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_local_llm_initialization(self, mock_tokenizer, mock_model):
        """Test local LLM initialization."""
        config = MagicMock()
        config.llm.model_path = "test_model"
        config.llm.model_type = "llama"

        LocalLLMInterface(config)
        mock_model.from_pretrained.assert_called_once_with("test_model", model_type="llama")

    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_local_llm_generation(self, mock_tokenizer, mock_model):
        """Test local LLM text generation."""
        config = MagicMock()
        config.llm.model_path = "test_model"
        config.llm.model_type = "llama"
        config.llm.max_tokens = 100
        config.llm.temperature = 0.7
        config.llm.stop_sequences = ["stop"]

        # Set up mock response
        mock_instance = mock_model.from_pretrained.return_value
        mock_instance.generate.return_value = [42]  # Token ID
        mock_tokenizer.from_pretrained.return_value.decode.return_value = "test response"

        interface = LocalLLMInterface(config)
        response = interface.generate("test prompt")

        assert response == "test response"
        mock_instance.generate.assert_called_once()

    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_local_llm_generation_error(self, mock_tokenizer, mock_model):
        """Test error handling in local LLM generation."""
        config = MagicMock()
        config.llm.model_path = "test_model"

        mock_instance = mock_model.from_pretrained.return_value
        mock_instance.generate.side_effect = Exception("Model error")

        interface = LocalLLMInterface(config)
        with pytest.raises(LLMResponseError):
            interface.generate("test prompt")
