"""
Safety Sandbox for PlainSpeak.

This module provides enhanced safety mechanisms for command execution.
"""
import os
import re
import shlex
import subprocess
from typing import List, Dict, Optional, Union, Tuple
import logging
from pathlib import Path
from .platform import platform_manager
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CommandContext:
    """Context information for command execution."""
    command: str
    cwd: str
    env: Dict[str, str]
    user: str
    timestamp: datetime
    platform: str

class SafetySandbox:
    """
    Enhanced safety sandbox for command execution.
    
    Features:
    - Command whitelisting/blacklisting
    - Resource limiting
    - Platform-specific safety checks
    - Detailed logging
    """
    
    # Commands that are never allowed
    BLACKLISTED_COMMANDS = {
        'rm -rf /',  # Prevent root deletion
        'dd',        # Raw disk operations
        'mkfs',      # Filesystem formatting
        ':(){:|:&}', # Fork bomb
        'wget',      # Arbitrary downloads (use controlled plugin instead)
        'curl',      # Arbitrary downloads (use controlled plugin instead)
    }
    
    # Patterns that indicate potentially dangerous operations
    DANGEROUS_PATTERNS = [
        r'\brm\s+(-[rf]\s+)*/*\s*$',  # Risky remove commands
        r'\b(dd|mkfs|fdisk)\b',        # Disk operations
        r'\b(wget|curl)\s+http',        # Arbitrary downloads
        r'>[>&]?(/etc|/dev|/sys)',     # Writing to system directories
        r'\b(chmod|chown)\s+[0-7]*777\b', # Overly permissive permissions
    ]
    
    # Resource limits (0 = unlimited)
    RESOURCE_LIMITS = {
        'MAX_CPU_TIME': 60,    # seconds
        'MAX_MEMORY': 512,     # MB
        'MAX_OUTPUT': 10_000,  # lines
        'MAX_PROCESSES': 10,   # subprocesses
    }
    
    def __init__(self):
        """Initialize the safety sandbox."""
        self.platform_mgr = platform_manager
            
    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a command is safe to execute.
        
        Args:
            command: The command to validate.
            
        Returns:
            Tuple of (is_safe, error_message).
        """
        # Check blacklisted commands
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return False, "Empty command"
            
        base_cmd = cmd_parts[0]
        
        # Check against blacklist
        if command in self.BLACKLISTED_COMMANDS:
            return False, f"Command '{command}' is blacklisted"
            
        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                return False, f"Command matches dangerous pattern: {pattern}"
                
        # Platform-specific path checks
        for part in cmd_parts:
            # Convert potential paths to normalized form
            if os.path.sep in part or '/' in part:
                if not self.platform_mgr.is_safe_path(part):
                    return False, f"Unsafe path: {part}"
                    
        return True, None
        
    def create_context(self, command: str) -> CommandContext:
        """
        Create execution context for a command.
        
        Args:
            command: The command to execute.
            
        Returns:
            CommandContext with execution details.
        """
        return CommandContext(
            command=self.platform_mgr.convert_command(command),
            cwd=os.getcwd(),
            env=os.environ.copy(),
            user=os.getlogin(),
            timestamp=datetime.now(),
            platform=self.platform_mgr.system
        )
        
    def execute_command(
        self,
        command: str,
        *,
        capture_output: bool = True,
        timeout: Optional[int] = None
    ) -> subprocess.CompletedProcess:
        """
        Safely execute a command.
        
        Args:
            command: The command to execute.
            capture_output: Whether to capture command output.
            timeout: Command timeout in seconds.
            
        Returns:
            CompletedProcess instance with execution results.
            
        Raises:
            ValueError: If the command fails validation.
            subprocess.TimeoutExpired: If the command times out.
            subprocess.CalledProcessError: If the command fails.
        """
        # Validate command
        is_safe, error = self.validate_command(command)
        if not is_safe:
            raise ValueError(f"Unsafe command: {error}")
            
        # Create execution context
        context = self.create_context(command)
        
        # Log execution
        logger.info(
            "Executing command: %s (user=%s, cwd=%s, platform=%s)",
            command, context.user, context.cwd, context.platform
        )
        
        # Set resource limits
        timeout = timeout or self.RESOURCE_LIMITS['MAX_CPU_TIME']
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=context.cwd,
                env=context.env
            )
            
            # Log success
            logger.info(
                "Command completed successfully: %s (returncode=%d)",
                command, result.returncode
            )
            
            return result
            
        except subprocess.TimeoutExpired as e:
            logger.error(
                "Command timed out after %d seconds: %s",
                timeout, command
            )
            raise
            
        except subprocess.CalledProcessError as e:
            logger.error(
                "Command failed with code %d: %s\nError: %s",
                e.returncode, command, e.stderr
            )
            raise
            
        except Exception as e:
            logger.error(
                "Unexpected error executing command: %s\nError: %s",
                command, str(e)
            )
            raise

# Global sandbox instance
sandbox = SafetySandbox()
