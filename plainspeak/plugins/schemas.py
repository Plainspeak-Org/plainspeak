"""
Pydantic schemas for PlainSpeak plugins.

This module defines the schemas used for plugin configuration validation.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator
import re


class CommandConfig(BaseModel):
    """Configuration for a single command."""

    template: str = Field(..., description="Jinja2 template for generating the command")
    description: str = Field(
        ..., description="Human-readable description of what the command does"
    )
    examples: List[str] = Field(
        default_factory=list, description="Example usages of the command"
    )
    required_args: List[str] = Field(
        default_factory=list, description="Arguments that must be provided"
    )
    optional_args: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Optional arguments with their default values"
    )

    @field_validator("template")
    def validate_template(cls, v: str) -> str:
        """Validate that the template contains valid placeholder syntax."""
        # Check for basic Jinja2 variable syntax
        if not re.search(r"{{\s*\w+\s*}}", v):
            raise ValueError(
                "Template must contain at least one variable placeholder ({{ var }})"
            )
        return v


class PluginManifest(BaseModel):
    """Schema for plugin manifest files."""

    name: str = Field(
        default=...,
        description="Unique name of the plugin",
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
    )
    description: str = Field(
        default=..., description="Human-readable description of the plugin"
    )
    version: str = Field(
        default=...,
        description="Plugin version (semver)",
        pattern=r"^\d+\.\d+\.\d+$"
    )
    author: str = Field(default=..., description="Plugin author")
    verbs: List[str] = Field(
        default=...,
        description="List of verbs this plugin provides",
        min_items=1
    )
    commands: Dict[str, CommandConfig] = Field(
        default=..., description="Command configurations keyed by verb"
    )
    dependencies: Dict[str, str] = Field(
        default_factory=dict, description="Plugin dependencies with version constraints"
    )
    entrypoint: str = Field(
        default=...,
        description="Python import path to the plugin class",
        pattern=r"^[a-zA-Z][a-zA-Z0-9_.]*[a-zA-Z0-9]$",
    )

    @field_validator("verbs")
    def validate_verbs(cls, v: List[str]) -> List[str]:
        """Validate that verbs are lowercase and contain no spaces."""
        for verb in v:
            if not verb.islower() or " " in verb:
                raise ValueError(
                    f"Verb '{verb}' must be lowercase and contain no spaces"
                )
        return v

    @field_validator("commands")
    def validate_commands(
        cls, v: Dict[str, CommandConfig], values: Dict[str, Any]
    ) -> Dict[str, CommandConfig]:  # type: ignore[misc]
        """Validate that all verbs have corresponding commands."""
        if "verbs" in values:
            missing = set(values["verbs"]) - set(v.keys())
            if missing:
                raise ValueError(
                    f"Missing command configurations for verbs: {', '.join(missing)}"
                )
        return v


class EntryPointConfig(BaseModel):
    """Configuration loaded from entry points."""

    manifest_path: str = Field(..., description="Path to the plugin manifest file")
    class_path: str = Field(..., description="Import path to the plugin class")


class PluginConfig(BaseModel):
    """Runtime configuration for a loaded plugin."""

    manifest: PluginManifest
    instance: Optional[Any] = Field(
        None, description="Instance of the plugin class once loaded"
    )
    enabled: bool = Field(True, description="Whether the plugin is currently enabled")
    load_error: Optional[str] = Field(
        None, description="Error message if plugin failed to load"
    )
