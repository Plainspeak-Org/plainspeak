# PlainSpeak Plugins Overview

PlainSpeak's functionality is organized into plugins, each providing a set of related capabilities. This document gives you an overview of the available plugins and how to use them.

## Core Plugins

The following plugins come pre-installed with PlainSpeak and provide essential functionality:

### File Plugin

**Purpose:** Interact with files and directories

**Key verbs:** find, list, copy, move, rename, delete, read, create

**Example commands:**
- "Find all PDF files in my documents folder modified in the last week"
- "List the largest files in my downloads folder"
- "Copy all images from the desktop to my backup folder"
- "Delete temporary files older than 30 days"

### System Plugin

**Purpose:** Interact with system resources and information

**Key verbs:** show, monitor, check, kill, restart

**Example commands:**
- "Show system information"
- "Monitor CPU usage"
- "Check available disk space"
- "Kill the process using port 8080"
- "Restart the web server"

### Network Plugin

**Purpose:** Perform network-related operations

**Key verbs:** ping, download, check, scan, connect

**Example commands:**
- "Ping google.com"
- "Download the latest release of TensorFlow"
- "Check if mywebsite.com is up"
- "Scan my local network for devices"
- "Connect to the office VPN"

### Git Plugin

**Purpose:** Work with Git repositories

**Key verbs:** clone, commit, push, pull, checkout, status

**Example commands:**
- "Clone the React repository"
- "Commit all changes with message 'Update documentation'"
- "Push my changes to the main branch"
- "Check the status of my repository"
- "Create and switch to a new branch called feature-login"

### Text Plugin

**Purpose:** Process and manipulate text content

**Key verbs:** search, replace, count, extract, format

**Example commands:**
- "Search for 'TODO' in all JavaScript files"
- "Replace all occurrences of 'old_name' with 'new_name' in this file"
- "Count lines of code in Python files"
- "Extract all email addresses from this log file"
- "Format this JSON file to be human-readable"

## Extended Plugins

These plugins provide additional functionality and are included with PlainSpeak but may require additional configuration:

### Email Plugin

**Purpose:** Send and receive emails

**Key verbs:** send, read, check, search, attach

**Example commands:**
- "Send an email to john@example.com with subject 'Meeting notes'"
- "Read my latest unread emails"
- "Search my inbox for emails from Amazon"
- "Check if I have any new emails from my boss"

**Configuration:**
```toml
[plugins.email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
imap_server = "imap.gmail.com"
imap_port = 993
username = "your.email@gmail.com"
password = "your-app-password"  # Use app passwords for Gmail
```

### Calendar Plugin

**Purpose:** Manage calendar events and appointments

**Key verbs:** add, list, show, remind, cancel

**Example commands:**
- "Add a meeting with John tomorrow at 2pm"
- "Show my calendar for next week"
- "List all upcoming appointments"
- "Cancel my meeting with Sarah on Friday"

**Configuration:**
```toml
[plugins.calendar]
calendar_path = "~/.config/plainspeak/calendar.ics"
# Or for online calendars:
provider = "google"
credentials_file = "~/.config/plainspeak/calendar_credentials.json"
```

### Archive Plugin

**Purpose:** Compress and extract archive files

**Key verbs:** compress, extract, zip, unzip, create, backup

**Example commands:**
- "Compress the projects folder into a zip file"
- "Extract the contents of archive.tar.gz"
- "Create a backup of my documents folder"
- "Unzip all zip files in the downloads folder"

### Database Plugin

**Purpose:** Work with databases

**Key verbs:** query, backup, restore, export, import

**Example commands:**
- "Backup my MySQL database"
- "Run a SQL query on my database"
- "Export the users table to CSV"
- "Show all tables in my PostgreSQL database"

**Configuration:**
```toml
[plugins.database]
default_engine = "sqlite"
sqlite_path = "~/.config/plainspeak/data.db"
# For MySQL/PostgreSQL:
host = "localhost"
port = 3306
username = "user"
password = "password"
database = "mydatabase"
```

## Using Plugins

### Specifying a Plugin

You can explicitly specify which plugin to use by prefixing your command:

```
git plugin: push my changes to the remote repository
file plugin: find large PDF files in my documents folder
```

### Checking Available Plugins

To see all available plugins and their verbs:

```
plainspeak plugins list
```

To get help for a specific plugin:

```
plainspeak help git
```

## Installing Additional Plugins

### From PyPI

```bash
pip install plainspeak-plugin-name
```

### From a Local File

1. Download or create a plugin file (YAML or Python)
2. Place it in the plugins directory:
   ```bash
   cp my-plugin.yaml ~/.config/plainspeak/plugins/
   ```
3. Restart PlainSpeak

## Creating Your Own Plugins

See the [Plugin Development Guide](../../dev_docs/plugins/development.md) for information on creating your own plugins.

## Plugin Configuration

Configure plugins in your PlainSpeak configuration file:

```toml
[plugins.git]
default_branch = "main"
ssh_key = "~/.ssh/id_rsa"

[plugins.network]
default_timeout = 5
user_agent = "PlainSpeak/1.0"
```

Global plugin settings:

```toml
[plugins]
disabled = ["email", "calendar"]  # Disable specific plugins
enabled_only = false  # When true, only explicitly enabled plugins are loaded
directory = "~/.config/plainspeak/plugins"  # Custom plugin directory
``` 