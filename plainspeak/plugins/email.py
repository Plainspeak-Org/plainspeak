"""
Email Plugin for PlainSpeak.

This module provides email operations through natural language.
"""

import email
import email.utils
import getpass
import imaplib
import json
import os
import re
import smtplib
from email import policy
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import keyring  # type: ignore

from .base import YAMLPlugin, registry
from .platform import platform_manager


class EmailConfig:
    """Configuration for email accounts."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize email configuration.

        Args:
            config_path: Path to config file. If None, uses ~/.plainspeak/email.json
        """
        if config_path is None:
            config_path = Path.home() / ".plainspeak" / "email.json"

        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:  # type: ignore[no-any-return]  # type: ignore[no-any-return]
        """Load configuration from file."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path) as f:
            return json.load(f)

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def set_account(
        self,
        email: str,
        smtp_server: str,
        imap_server: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Configure an email account.

        Args:
            email: Email address
            smtp_server: SMTP server hostname
            imap_server: IMAP server hostname
            username: Optional username if different from email
            password: Optional password (if not provided, will prompt)
        """
        if password is None:
            password = getpass.getpass(f"Password for {email}: ")

        # Store password securely
        keyring.set_password("plainspeak_email", email, password)

        self.config[email] = {
            "smtp_server": smtp_server,
            "imap_server": imap_server,
            "username": username or email,
        }
        self._save_config()

    def get_account(self, email: str) -> Tuple[str, str, str, str]:
        """
        Get account configuration.

        Args:
            email: Email address

        Returns:
            Tuple of (username, password, smtp_server, imap_server)

        Raises:
            KeyError: If account not found
        """
        if email not in self.config:
            raise KeyError(f"No configuration found for {email}")

        acc = self.config[email]
        password = keyring.get_password("plainspeak_email", email)
        if not password:
            raise KeyError(f"No stored password for {email}")

        return (acc["username"], password, acc["smtp_server"], acc["imap_server"])


class EmailClient:
    """Email client for sending and reading emails."""

    def __init__(self, config: EmailConfig):
        """
        Initialize email client.

        Args:
            config: Email configuration
        """
        self.config = config
        self.smtp: Optional[smtplib.SMTP] = None
        self.imap: Optional[imaplib.IMAP4] = None

    def connect(self, email: str) -> None:
        """
        Connect to email servers.

        Args:
            email: Email address to use
        """
        username, password, smtp_server, imap_server = self.config.get_account(email)

        # Connect to SMTP
        self.smtp = smtplib.SMTP(smtp_server)
        self.smtp.starttls()
        self.smtp.login(username, password)

        # Connect to IMAP
        self.imap = imaplib.IMAP4_SSL(imap_server)
        self.imap.login(username, password)

    def disconnect(self) -> None:
        """Disconnect from email servers."""
        if self.smtp:
            self.smtp.quit()
            self.smtp = None

        if self.imap:
            self.imap.logout()
            self.imap = None

    def send_email(
        self,
        to: str,
        subject: str = "",
        body: str = "",
        attachments: Optional[List[str]] = None,
    ) -> None:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachments: Optional list of file paths to attach
        """
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["To"] = to

        # Add body
        msg.attach(MIMEText(body))

        # Add attachments
        if attachments:
            for path in attachments:
                with open(path, "rb") as f:
                    part = MIMEApplication(f.read())
                    part.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=os.path.basename(path),
                    )
                    msg.attach(part)

        if self.smtp:
            self.smtp.send_message(msg)

    def list_emails(self, folder: str = "INBOX", limit: int = 10, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        List emails in a folder.

        Args:
            folder: Folder name
            limit: Maximum number of emails to return
            unread_only: Only show unread emails

        Returns:
            List of email metadata dictionaries
        """
        if not self.imap:
            return []

        self.imap.select(folder)
        search_criteria = ["ALL"]
        if unread_only:
            search_criteria = ["UNSEEN"]

        _, message_numbers = self.imap.search(None, *search_criteria)
        emails = []

        for num in message_numbers[0].split()[-limit:]:
            _, msg_data = self.imap.fetch(num, "(RFC822)")
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body, policy=policy.default)

            emails.append(
                {
                    "id": num.decode(),
                    "subject": message["subject"],
                    "from": message["from"],
                    "date": message["date"],
                    "unread": "\\Seen" not in self.imap.fetch(num, "(FLAGS)")[1][0].decode(),
                }
            )

        return emails

    def read_email(
        self, id: Optional[str] = None, index: int = 1, mark_read: bool = True
    ) -> Optional[Dict[str, str]]:  # type: ignore[no-any-return]
        """
        Read a specific email.

        Args:
            id: Email ID
            index: Email index (1 = latest)
            mark_read: Whether to mark as read

        Returns:
            Email data dictionary or None if not found
        """
        if not self.imap:
            return None

        try:
            self.imap.select("INBOX")

            # Get message ID
            msg_id_str = ""
            if id is None:
                status, message_numbers = self.imap.search(None, "ALL")
                if status != "OK" or not message_numbers or not message_numbers[0]:
                    return None

                msg_ids = message_numbers[0].split()
                if not msg_ids or index > len(msg_ids):
                    return None

                # Get by index from the end (newest first)
                msg_id_bytes = msg_ids[-index]
                msg_id_str = msg_id_bytes.decode("utf-8")
            else:
                msg_id_str = id

            # Fetch the message
            status, data = self.imap.fetch(msg_id_str, "(RFC822)")
            if status != "OK" or not data:
                return None

            # Check first item in the data
            if not isinstance(data, list) or len(data) == 0:
                return None

            # Get the first item - this should be where the email data is
            first_item = data[0]  # type: ignore[index]
            if not isinstance(first_item, tuple) or len(first_item) < 2:
                return None

            # Extract the message content
            message_bytes = first_item[1]
            if not isinstance(message_bytes, bytes):
                return None

            # Parse the email without policy parameter
            message = email.message_from_bytes(message_bytes)  # type: ignore[arg-type]

            # Extract body content
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload is not None and isinstance(payload, bytes):
                            body = payload.decode("utf-8", errors="replace")  # type: ignore[union-attr]
                        break
            else:
                payload = message.get_payload(decode=True)
                if payload is not None and isinstance(payload, bytes):
                    body = payload.decode("utf-8", errors="replace")  # type: ignore[union-attr]

            # Mark as read if needed
            if mark_read:
                self.imap.store(msg_id_str, "+FLAGS", "\\Seen")

            # Build the result
            return {
                "subject": str(message.get("subject", "")),
                "from": str(message.get("from", "")),
                "to": str(message.get("to", "")),
                "date": str(message.get("date", "")),
                "body": body,
            }

        except Exception as e:
            import logging

            logging.error(f"Error reading email: {e}")
            return None

    def search_emails(self, query: str, folder: str = "INBOX", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails.

        Args:
            query: Search query
            folder: Folder to search
            limit: Maximum results

        Returns:
            List of matching email metadata
        """
        if not self.imap:
            return []

        self.imap.select(folder)

        # Convert natural query to IMAP search criteria
        search_criteria = []
        if "@" in query:  # Looks like an email address
            search_criteria.extend(["OR", "FROM", query, "TO", query])
        else:
            search_criteria.extend(["OR", "SUBJECT", query, "BODY", query])

        _, message_numbers = self.imap.search(None, *search_criteria)
        return self.list_emails(limit=limit)


class EmailPlugin(YAMLPlugin):
    """
    Plugin for email operations.

    Features:
    - Email account configuration
    - Sending emails with attachments
    - Reading and searching emails
    - IMAP folder management
    """

    def __init__(self):
        """Initialize the email plugin."""
        yaml_path = Path(__file__).parent / "email.yaml"
        super().__init__(yaml_path)

        self.config = EmailConfig()
        self.client = EmailClient(self.config)

    def _preprocess_args(self, verb: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess command arguments.

        Args:
            verb: The verb being used.
            args: Original arguments.

        Returns:
            Processed arguments.
        """
        processed = args.copy()

        # Handle email addresses
        if "to" in processed:
            # Try to extract email from natural text
            text = processed["to"]
            matches = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
            if matches:
                processed["to"] = matches[0]

        # Handle attachments
        if "attachment" in processed:
            path = processed["attachment"]
            if path:
                processed["attachment"] = platform_manager.convert_path_for_command(path)

        return processed

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate an email command.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.
        """
        # Preprocess arguments
        args = self._preprocess_args(verb, args)

        # Generate command using parent's implementation
        return super().generate_command(verb, args)


# Create and register the plugin instance
try:
    email_plugin = EmailPlugin()
    registry.register(email_plugin)
except Exception as e:
    # Log error but don't prevent other plugins from loading
    import logging

    logger = logging.getLogger(__name__)
    logger.warning("Failed to load Email plugin: %s", str(e))
