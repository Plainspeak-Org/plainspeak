"""
Pydantic schemas for PlainSpeak plugins.

This module defines the schemas used for plugin configuration validation.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class VerbDetails(BaseModel):
    """Details about a verb's implementation."""

    template: str
    parameters_schema: Dict[str, Dict[str, Any]]
    aliases: List[str] = Field(default_factory=list)


class CommandConfig(BaseModel):
    """Configuration for a single command."""

    template: str = Field(..., description="Jinja2 template for generating the command")
    description: str = Field(..., description="Human-readable description of what the command does")
    examples: List[str] = Field(default_factory=list, description="Example usages of the command")
    required_args: List[str] = Field(default_factory=list, description="Arguments that must be provided")
    optional_args: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, description="Optional arguments with their default values"
    )
    aliases: List[str] = Field(
        default_factory=list,
        description="Alternative verbs that can be used to invoke this command",
    )


class PluginManifest(BaseModel):
    """Schema for plugin manifest files."""

    name: str = Field(  # type: ignore[call-overload]
        default=...,  # Use default= instead of positional argument
        description="Unique name of the plugin",
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
    )
    description: str = Field(  # type: ignore[call-overload]
        default=..., description="Human-readable description of the plugin"
    )
    version: str = Field(  # type: ignore[call-overload]
        default=...,
        description="Plugin version (semver)",
        pattern=r"^\d+\.\d+\.\d+$",
    )
    author: str = Field(default=..., description="Plugin author")  # type: ignore[call-overload]
    verbs: List[str] = Field(  # type: ignore[call-overload]
        default=..., description="List of verbs this plugin provides", min_length=1
    )
    commands: Dict[str, CommandConfig] = Field(  # type: ignore[call-overload]
        default=..., description="Command configurations keyed by verb"
    )
    dependencies: Dict[str, str] = Field(
        default_factory=dict, description="Plugin dependencies with version constraints"
    )
    entrypoint: str = Field(  # type: ignore[call-overload]
        default=...,
        description="Python import path to the plugin class",
        pattern=r"^[a-zA-Z][a-zA-Z0-9_.]*[a-zA-Z0-9]$",
    )
    priority: int = Field(
        default=0,
        description="Plugin priority (higher values indicate higher priority)",
        ge=0,
        le=100,
    )
    verb_aliases: Dict[str, List[str]] = Field(
        default_factory=dict, description="Mapping of verb aliases to canonical verbs"
    )

    @field_validator("verbs")
    def validate_verbs(cls, v: List[str]) -> List[str]:
        """Validate that verbs are lowercase and contain no spaces."""
        for verb in v:
            if not verb.islower() or " " in verb:
                raise ValueError(f"Verb '{verb}' must be lowercase and contain no spaces")
        return v

    @field_validator("commands")  # type: ignore
    def validate_commands(
        cls, v: Dict[str, CommandConfig], info: ValidationInfo
    ) -> Dict[str, CommandConfig]:  # type: ignore[misc]
        """Validate that all verbs have corresponding commands."""
        if "verbs" in info.data and isinstance(info.data["verbs"], list):
            verbs_data = info.data["verbs"]
            missing = set(verbs_data) - set(v.keys())
            if missing:
                raise ValueError(f"Missing command configurations for verbs: {', '.join(missing)}")
        return v

    @field_validator("verb_aliases")
    def validate_verb_aliases(cls, v: Dict[str, List[str]], info: ValidationInfo) -> Dict[str, List[str]]:
        """Validate that all canonical verbs in verb_aliases exist in verbs."""
        if "verbs" in info.data and isinstance(info.data["verbs"], list):
            verbs_data = info.data["verbs"]
            for canonical_verb, aliases in v.items():
                if canonical_verb not in verbs_data:
                    raise ValueError(f"Canonical verb '{canonical_verb}' in verb_aliases is not defined in verbs")
                for alias in aliases:
                    if not alias.islower() or " " in alias:
                        raise ValueError(f"Verb alias '{alias}' must be lowercase and contain no spaces")
        return v


class EntryPointConfig(BaseModel):
    """Configuration loaded from entry points."""

    manifest_path: str = Field(..., description="Path to the plugin manifest file")
    class_path: str = Field(..., description="Import path to the plugin class")


class PluginConfig(BaseModel):
    """Runtime configuration for a loaded plugin."""

    manifest: PluginManifest
    instance: Optional[Any] = Field(None, description="Instance of the plugin class once loaded")
    enabled: bool = Field(True, description="Whether the plugin is currently enabled")
    load_error: Optional[str] = Field(None, description="Error message if plugin failed to load")
