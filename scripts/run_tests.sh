#!/bin/bash

# Run the fixed tests
poetry run pytest tests/test_core tests/test_i18n.py tests/test_remote_llm.py tests/test_assets.py tests/test_config.py tests/test_context.py tests/test_cli_compat.py tests/test_learning.py tests/test_llm_interface_compat.py tests/test_end_to_end_compat.py tests/test_integration_compat.py tests/test_parser_compat.py tests/test_plugin_registry_compat.py tests/test_plugin_verb_matching_compat.py tests/test_plugin_verb_matching_integration_compat.py tests/test_prompts_compat.py tests/test_binary_compat.py tests/test_plugins/test_dataspeak_compat.py tests/test_plugins/test_yaml_plugin_compat.py "$@"
