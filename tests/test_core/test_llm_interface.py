from unittest.mock import MagicMock, patch

import pytest
import requests  # Added import

from plainspeak.config import LLMConfig, PlainSpeakConfig
from plainspeak.context import PlainSpeakContext
from plainspeak.core.llm import LLMInterface, LLMResponseError, LocalLLMInterface, RemoteLLMInterface


@pytest.fixture
def mock_base_config():
    config = MagicMock(spec=PlainSpeakConfig)
    config.llm = MagicMock(spec=LLMConfig)
    config.llm.provider = "local"  # Default to local for some tests
    config.llm.model_path = "dummy/path/to/model.gguf"
    config.llm.api_key_env_var = "TEST_API_KEY"
    config.llm.remote_url = "http://localhost:8080/completion"
    config.llm.prompt_template = "Instruction: {instruction}\nUser: {text}\nAssistant:"
    config.llm.max_tokens = 150
    config.llm.temperature = 0.1
    config.llm.stop_sequences = ["\nUser:", "</s>"]
    config.llm.default_llm_instruction = "Parse the user input into a JSON command."
    return config


@pytest.fixture
def mock_context():
    ctx = MagicMock(spec=PlainSpeakContext)
    ctx.get_llm_instruction.return_value = "Parse the user input into a JSON command."
    return ctx


class TestLLMInterface:
    def test_llm_interface_init(self, mock_base_config):
        interface = LLMInterface(mock_base_config)
        assert interface.config == mock_base_config
        assert interface.llm_config == mock_base_config.llm

    def test_llm_interface_parse_intent_not_implemented(self, mock_base_config, mock_context):
        interface = LLMInterface(mock_base_config)
        with pytest.raises(NotImplementedError):
            interface.parse_intent("test command", mock_context)

    def test_prepare_prompt(self, mock_base_config, mock_context):
        interface = LLMInterface(mock_base_config)
        text = "list files in /tmp"
        instruction = "Extract command details."
        mock_context.get_llm_instruction.return_value = instruction

        prompt = interface._prepare_prompt(text, mock_context)

        expected_prompt = mock_base_config.llm.prompt_template.format(instruction=instruction, text=text)
        assert prompt == expected_prompt
        mock_context.get_llm_instruction.assert_called_once()

    def test_parse_llm_response_valid_json(self, mock_base_config):
        interface = LLMInterface(mock_base_config)
        raw_response_text = '{"verb": "list", "plugin": "file", "parameters": {"path": "/tmp"}}'
        expected_ast = {"verb": "list", "plugin": "file", "parameters": {"path": "/tmp"}}

        ast = interface._parse_llm_response(raw_response_text, "test command")
        assert ast == expected_ast

    def test_parse_llm_response_json_with_markdown_fences(self, mock_base_config):
        interface = LLMInterface(mock_base_config)
        raw_response_text = '```json\n{"verb": "list", "plugin": "file"}\n```'
        expected_ast = {"verb": "list", "plugin": "file"}
        ast = interface._parse_llm_response(raw_response_text, "test command")
        assert ast == expected_ast

    def test_parse_llm_response_invalid_json(self, mock_base_config):
        interface = LLMInterface(mock_base_config)
        raw_response_text = "this is not json"
        with pytest.raises(LLMResponseError, match="Failed to decode LLM JSON response"):
            interface._parse_llm_response(raw_response_text, "test command")

    def test_parse_llm_response_empty(self, mock_base_config):
        interface = LLMInterface(mock_base_config)
        raw_response_text = ""
        with pytest.raises(LLMResponseError, match="LLM response was empty"):
            interface._parse_llm_response(raw_response_text, "test command")


class TestLocalLLMInterface:
    @patch("ctransformers.AutoModel.from_pretrained")
    def test_local_llm_init_successful(self, mock_from_pretrained, mock_base_config):
        mock_model_instance = MagicMock()
        mock_from_pretrained.return_value = mock_model_instance

        llm_interface = LocalLLMInterface(mock_base_config)

        assert llm_interface.model == mock_model_instance
        mock_from_pretrained.assert_called_once_with(
            mock_base_config.llm.model_path,
            model_type=mock_base_config.llm.model_type,
            # Add other ctransformers AutoModel params if configured and passed
        )

    @patch("ctransformers.AutoModel.from_pretrained", side_effect=Exception("Model load failed"))
    def test_local_llm_init_failure(self, mock_from_pretrained_error, mock_base_config):
        with pytest.raises(RuntimeError, match="Failed to load local LLM model"):
            LocalLLMInterface(mock_base_config)

    @patch("ctransformers.AutoModel.from_pretrained")
    def test_local_llm_parse_intent_successful(self, mock_from_pretrained, mock_base_config, mock_context):
        mock_model = MagicMock()
        mock_model.return_value = (
            '{"verb": "show", "plugin": "system", "parameters": {"item": "time"}}'  # Simulate model __call__
        )
        mock_from_pretrained.return_value = mock_model

        interface = LocalLLMInterface(mock_base_config)

        # Ensure _prepare_prompt is patchable on the instance or class for testing this part
        with patch.object(LocalLLMInterface, "_prepare_prompt", return_value="Prepared Prompt") as mock_prepare_prompt:
            ast = interface.parse_intent("show time", mock_context)

        mock_prepare_prompt.assert_called_once_with("show time", mock_context)
        mock_model.assert_called_once_with(
            "Prepared Prompt",
            max_new_tokens=mock_base_config.llm.max_tokens,
            temperature=mock_base_config.llm.temperature,
            stop=mock_base_config.llm.stop_sequences,
            # Add other ctransformers generation params if configured
        )
        assert ast == {"verb": "show", "plugin": "system", "parameters": {"item": "time"}}

    @patch("ctransformers.AutoModel.from_pretrained")
    def test_local_llm_parse_intent_model_error(self, mock_from_pretrained, mock_base_config, mock_context):
        mock_model = MagicMock(side_effect=Exception("Model generation error"))
        mock_from_pretrained.return_value = mock_model

        interface = LocalLLMInterface(mock_base_config)
        with pytest.raises(LLMResponseError, match="Local LLM generation failed"):
            interface.parse_intent("some command", mock_context)


class TestRemoteLLMInterface:
    @patch.dict("os.environ", {"TEST_API_KEY": "fake_api_key_from_env"})
    def test_remote_llm_init_api_key_from_env(self, mock_base_config):
        mock_base_config.llm.provider = "remote"
        mock_base_config.llm.api_key = None  # Ensure it tries to load from env
        mock_base_config.llm.api_key_env_var = "TEST_API_KEY"

        interface = RemoteLLMInterface(mock_base_config)
        assert interface.api_key == "fake_api_key_from_env"

    def test_remote_llm_init_api_key_direct(self, mock_base_config):
        mock_base_config.llm.provider = "remote"
        mock_base_config.llm.api_key = "direct_fake_key"
        mock_base_config.llm.api_key_env_var = "UNUSED_ENV_VAR"  # Should be ignored

        interface = RemoteLLMInterface(mock_base_config)
        assert interface.api_key == "direct_fake_key"

    @patch.dict("os.environ", clear=True)  # Ensure TEST_API_KEY is not set
    def test_remote_llm_init_api_key_missing(self, mock_base_config):
        mock_base_config.llm.provider = "remote"
        mock_base_config.llm.api_key = None
        mock_base_config.llm.api_key_env_var = "MISSING_TEST_API_KEY"

        with pytest.raises(ValueError, match="API key for remote LLM not found."):
            RemoteLLMInterface(mock_base_config)

    @patch("requests.post")
    def test_remote_llm_parse_intent_successful(self, mock_post, mock_base_config, mock_context):
        mock_base_config.llm.provider = "remote"
        mock_base_config.llm.api_key = "testkey"  # Direct key for simplicity here

        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulate a JSON response that _parse_llm_response can handle
        mock_response.text = '{"verb": "search", "plugin": "web", "parameters": {"query": "cats"}}'
        mock_post.return_value = mock_response

        interface = RemoteLLMInterface(mock_base_config)

        with patch.object(
            RemoteLLMInterface, "_prepare_prompt", return_value="Remote Prepared Prompt"
        ) as mock_prepare_prompt:
            ast = interface.parse_intent("search for cats", mock_context)

        mock_prepare_prompt.assert_called_once_with("search for cats", mock_context)

        expected_payload = {
            "prompt": "Remote Prepared Prompt",
            "max_tokens": mock_base_config.llm.max_tokens,
            "temperature": mock_base_config.llm.temperature,
            "stop": mock_base_config.llm.stop_sequences,
            # Add other parameters if RemoteLLMInterface sends them
        }
        expected_headers = {"Authorization": f"Bearer {interface.api_key}", "Content-Type": "application/json"}
        mock_post.assert_called_once_with(
            mock_base_config.llm.remote_url,
            json=expected_payload,
            headers=expected_headers,
            timeout=interface.llm_config.remote_timeout,
        )
        assert ast == {"verb": "search", "plugin": "web", "parameters": {"query": "cats"}}

    @patch("requests.post")
    def test_remote_llm_parse_intent_http_error(self, mock_post, mock_base_config, mock_context):
        mock_base_config.llm.provider = "remote"
        mock_base_config.llm.api_key = "testkey"

        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_response.text = '{"error": "Invalid API Key"}'
        mock_post.return_value = mock_response

        interface = RemoteLLMInterface(mock_base_config)
        with pytest.raises(LLMResponseError, match="Remote LLM API request failed with status 401"):
            interface.parse_intent("some command", mock_context)

    @patch("requests.post", side_effect=requests.exceptions.RequestException("Network Error"))
    def test_remote_llm_parse_intent_network_error(self, mock_post_error, mock_base_config, mock_context):
        mock_base_config.llm.provider = "remote"
        mock_base_config.llm.api_key = "testkey"

        interface = RemoteLLMInterface(mock_base_config)
        with pytest.raises(LLMResponseError, match="Remote LLM API request failed due to network error: Network Error"):
            interface.parse_intent("some command", mock_context)
