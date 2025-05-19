"""
Internationalization (i18n) module for PlainSpeak.

This module provides functionality for loading and managing translations
for different languages and locales.
"""

import json
import locale
import os
from typing import Any, Dict, List, Optional

# Default locale used as fallback
DEFAULT_LOCALE = "en_US"


def get_locale() -> str:
    """
    Get the current system locale.

    Returns:
        The current locale code (e.g., "en_US").
    """
    try:
        # Get current locale
        current_locale, _ = locale.getlocale()

        # If no locale is detected, fall back to default
        if not current_locale:
            return DEFAULT_LOCALE

        return current_locale
    except Exception:
        # If there's any error, fall back to default
        return DEFAULT_LOCALE


def set_locale(locale_code: str) -> bool:
    """
    Set the system locale.

    Args:
        locale_code: The locale code to set (e.g., "en_US").

    Returns:
        True if the locale was set successfully, False otherwise.
    """
    try:
        locale.setlocale(locale.LC_ALL, locale_code)
        return True
    except locale.Error:
        # If the locale is not supported, return False
        return False


def available_locales() -> List[str]:
    """
    Get a list of available locales on the system.

    Returns:
        List of available locale codes.
    """
    # In CI environments or restricted systems, we may not be able to check
    # all locales by setting them. Instead, we'll return a minimal set of
    # locales that should be available in most environments.

    # For testing purposes, always include at least these locales
    minimal_locales = [
        DEFAULT_LOCALE,  # en_US
        "C",  # The C locale should always be available
    ]

    # Try to get additional locales if possible
    try:
        # Try to get the current locale first
        current = locale.getlocale()
        current_loc = current[0] if current and current[0] else None

        if current_loc and current_loc not in minimal_locales:
            minimal_locales.append(current_loc)

        # Common locales that might be available
        common_locales = [
            "en_US",
            "en_GB",
            "fr_FR",
            "de_DE",
            "es_ES",
            "it_IT",
            "ja_JP",
            "ko_KR",
            "zh_CN",
            "zh_TW",
            "ru_RU",
            "pt_BR",
        ]

        # Try to find available locales without actually setting them
        # This is safer for CI environments
        for alias, loc_code in locale.locale_alias.items():
            if any(common in loc_code for common in common_locales):
                # Extract the main locale code (e.g., "en_US" from "en_US.UTF-8")
                main_code = loc_code.split(".")[0]
                if main_code and main_code not in minimal_locales:
                    minimal_locales.append(main_code)
    except Exception:
        # If anything goes wrong, just use the minimal set
        pass

    return minimal_locales


class I18n:
    """
    Internationalization class for managing translations.

    This class loads translations from JSON files and provides methods
    for retrieving translations in different languages.
    """

    def __init__(self, translations_dir: Optional[str] = None):
        """
        Initialize the I18n instance.

        Args:
            translations_dir: Directory containing translation files.
                If None, defaults to the "translations" directory in
                the same directory as this module.
        """
        # Set default translations directory if not provided
        if translations_dir is None:
            translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "translations")

        self.translations_dir = translations_dir
        self.locale = get_locale()

        # Dictionary to store translations for all locales
        self.translations: Dict[str, Dict[str, Any]] = {}

        # Load translations
        self.load_translations()

    def load_translations(self) -> None:
        """Load all translation files from the translations directory."""
        try:
            # Create translations directory if it doesn't exist
            os.makedirs(self.translations_dir, exist_ok=True)

            # Load each translation file
            for filename in os.listdir(self.translations_dir):
                if filename.endswith(".json"):
                    locale_code = filename[:-5]  # Remove .json extension
                    file_path = os.path.join(self.translations_dir, filename)

                    with open(file_path, "r", encoding="utf-8") as f:
                        try:
                            self.translations[locale_code] = json.load(f)
                        except json.JSONDecodeError:
                            # Skip invalid JSON files
                            continue
        except Exception:
            # If there's an error loading translations, create an empty default dict
            if DEFAULT_LOCALE not in self.translations:
                self.translations[DEFAULT_LOCALE] = {}

    def set_locale(self, locale_code: str) -> None:
        """
        Set the active locale.

        Args:
            locale_code: The locale code to set (e.g., "en_US").
        """
        self.locale = locale_code

    def get_locale(self) -> str:
        """
        Get the current active locale.

        Returns:
            The current locale code.
        """
        return self.locale

    def has_locale(self, locale_code: str) -> bool:
        """
        Check if translations for a specific locale are available.

        Args:
            locale_code: The locale code to check.

        Returns:
            True if translations for the locale are available, False otherwise.
        """
        return locale_code in self.translations

    def get_key(self, key: str, locale_code: Optional[str] = None) -> Any:
        """
        Get a translation value from the specified locale.

        Args:
            key: The translation key to retrieve.
            locale_code: The locale to use. If None, uses the current locale.

        Returns:
            The translation value, or the key itself if not found.
        """
        if locale_code is None:
            locale_code = self.locale

        # If the locale is not available, fall back to default
        if not self.has_locale(locale_code):
            locale_code = DEFAULT_LOCALE

        # If the default locale is not available, return the key
        if not self.has_locale(locale_code):
            return key

        # Get the translations for the locale
        translations = self.translations[locale_code]

        # Handle nested keys (e.g., "nested.key")
        if "." in key:
            parts = key.split(".")
            current = translations

            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return key

            return current

        # Handle simple keys
        return translations.get(key, key)

    def t(
        self,
        key: str,
        params: Optional[Dict[str, Any]] = None,
        locale_code: Optional[str] = None,
    ) -> str:
        """
        Get a translation with optional parameter substitution.

        Args:
            key: The translation key to retrieve.
            params: Optional parameters for substitution.
            locale_code: The locale to use. If None, uses the current locale.

        Returns:
            The translated string with parameters substituted.
        """
        # Get the translation value
        value = self.get_key(key, locale_code)

        # If the value is not a string, convert it to a string
        if not isinstance(value, str):
            value = str(value)

        # Substitute parameters
        if params:
            try:
                return value.format(**params)
            except (KeyError, ValueError):
                # If parameter substitution fails, return the original value
                return value

        return value
