"""
Natural Language Parser for PlainSpeak.

This module provides functionality for parsing natural language into
structured commands using LLM models.
"""

import os
import json
from typing import Dict, Any, Optional, List, Tuple

from .llm import LLMInterface
from .i18n import I18n


class NaturalLanguageParser:
    """
    Parser for converting natural language to structured commands.
    
    This class uses an LLM to parse natural language input into a structured
    format with a verb and arguments.
    """
    
    def __init__(self, llm: LLMInterface, i18n: Optional[I18n] = None):
        """
        Initialize the parser.
        
        Args:
            llm: LLM interface for natural language processing.
            i18n: Optional I18n instance for internationalization.
        """
        self.llm = llm
        self.i18n = i18n
        
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language text into a structured command.
        
        Args:
            text: The natural language text to parse.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not text:
            return {"verb": None, "args": {}}
            
        # Use locale-specific parsing if i18n is available
        if self.i18n:
            locale = self.i18n.get_locale()
            return self.parse_with_locale(text, locale)
            
        # Fall back to standard parsing
        return self.llm.parse_natural_language(text)
        
    def parse_with_locale(self, text: str, locale: str) -> Dict[str, Any]:
        """
        Parse natural language text using locale-specific context.
        
        Args:
            text: The natural language text to parse.
            locale: The locale to use for parsing.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not text:
            return {"verb": None, "args": {}}
            
        # Use locale-specific parsing if available
        if hasattr(self.llm, "parse_natural_language_with_locale"):
            return self.llm.parse_natural_language_with_locale(text, locale)
            
        # Fall back to standard parsing
        return self.llm.parse_natural_language(text)
        
    def get_examples(self, locale: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get examples of natural language commands and their structured output.
        
        Args:
            locale: Optional locale code to get language-specific examples.
            
        Returns:
            List of example dictionaries with "input" and "output" fields.
        """
        # Default locale if not specified
        if locale is None and self.i18n:
            locale = self.i18n.get_locale()
        elif locale is None:
            locale = "en_US"
            
        # Try to load examples for the specified locale
        examples_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "examples",
            f"{locale}.json"
        )
        
        try:
            if os.path.exists(examples_path):
                with open(examples_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
            
        # Fall back to English examples
        fallback_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "examples",
            "en_US.json"
        )
        
        try:
            if os.path.exists(fallback_path):
                with open(fallback_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
            
        # If no examples are found, return a simple default set
        return [
            {
                "input": "list files",
                "output": {"verb": "ls", "args": {"path": "."}}
            },
            {
                "input": "find all text files",
                "output": {"verb": "find", "args": {"path": ".", "pattern": "*.txt"}}
            },
            {
                "input": "show running processes",
                "output": {"verb": "ps", "args": {}}
            }
        ]
        
    def get_verb_suggestions(self, text: str) -> List[str]:
        """
        Get suggestions for verbs based on partial input.
        
        Args:
            text: Partial or complete natural language input.
            
        Returns:
            List of suggested verbs.
        """
        # Use LLM to suggest verbs
        if hasattr(self.llm, "suggest_verbs"):
            return self.llm.suggest_verbs(text)
            
        # Simple fallback if LLM doesn't support verb suggestions
        common_verbs = [
            "list", "find", "search", "show", "create", "edit",
            "delete", "copy", "move", "rename", "download"
        ]
        
        # Filter verbs that match the beginning of the text
        if text:
            text_lower = text.lower()
            return [verb for verb in common_verbs if verb.startswith(text_lower)]
            
        return common_verbs
        
    def extract_key_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract key entities from natural language text.
        
        This is useful for highlighting or providing contextual help.
        
        Args:
            text: Natural language text.
            
        Returns:
            Dictionary of entity types to values.
        """
        if hasattr(self.llm, "extract_entities"):
            return self.llm.extract_entities(text)
            
        # Simple fallback extraction
        entities = {}
        words = text.split()
        
        # Extract potential file paths
        for word in words:
            if "/" in word or "." in word:
                if "files" not in entities:
                    entities["files"] = []
                entities["files"].append(word)
                
        # Extract potential options (words starting with -)
        options = [word for word in words if word.startswith("-")]
        if options:
            entities["options"] = options
            
        return entities 