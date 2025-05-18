# PlainSpeak Advanced Usage Tips

This guide provides advanced techniques and tips for power users to get the most out of PlainSpeak.

## Command Line Efficiency

### Piping and Redirection

You can include piping and redirection in your natural language commands:

```bash
# Piping example
plainspeak "find all logs from yesterday and extract error messages"

# Redirection example
plainspeak "find large files and save the list to disk_usage.txt"
```

### Session Management

Control your PlainSpeak sessions for better organization:

```bash
# Start a named session
plainspeak shell --session-name "data-analysis"

# List active sessions
plainspeak sessions list

# Resume a specific session
plainspeak shell --session-name "data-analysis"

# Export session history
plainspeak sessions export "data-analysis" --output ~/my-session-log.txt
```

### Command History Navigation

Advanced history manipulation:

```bash
# Search history with fuzzy matching
plainspeak history search "file operation"

# Replay a specific command from history
plainspeak history replay 42

# Modify and replay a command
plainspeak history modify 42 "with different parameters"
```

## Advanced Plugin Usage

### Plugin Chaining

Chain multiple plugins together for complex operations:

```bash
# Combine git and file operations
plainspeak "find all modified JavaScript files and stage them for commit"

# Mix network and file operations
plainspeak "download yesterday's logs from the server and extract error counts"
```

### Plugin Priority Control

Force specific plugin selection when verbs might be ambiguous:

```bash
# Explicitly use the file plugin's 'find' verb
plainspeak "file plugin: find large images"

# Explicitly use the network plugin
plainspeak "network plugin: download the latest data"
```

### Creating Custom Plugin Aliases

Define your own shorthand commands for frequently used operations:

```bash
# Define a custom alias
plainspeak alias create "proj-setup" "git clone {1} && cd {1} && npm install"

# Use the alias
plainspeak "proj-setup https://github.com/user/repo"
```

## Context and Environment

### Environment-Aware Commands

Make PlainSpeak aware of your development environment:

```bash
# Set project context
plainspeak context set --project-type "react" --root "/path/to/project"

# Commands will now be interpreted with React project context
plainspeak "start development server"
```

### Context Variables

Use variables to make commands more flexible:

```bash
# Set context variables
plainspeak set SERVER_URL="https://api.example.com"
plainspeak set ENV="production"

# Use variables in commands
plainspeak "ping $SERVER_URL and check status"
```

## Advanced Data Operations with DataSpeak

### Complex Queries

Perform sophisticated data analysis with natural language:

```bash
# Complex filtering and aggregation
plainspeak "show me sales by region where profit margin exceeds 20% for the last quarter"

# Temporal analysis
plainspeak "plot the trend of website traffic by hour of day and highlight peak times"

# Comparative analysis
plainspeak "compare customer retention rates between premium and basic subscribers"
```

### Advanced Visualization

Create tailored visualizations for your data:

```bash
# Customized charts
plainspeak "create a stacked bar chart of revenue by product category and region"

# Multiple visualizations
plainspeak "show me customer age distribution as both a histogram and box plot"

# Interactive dashboards
plainspeak "build a dashboard with sales trends, customer demographics, and inventory levels"
```

### Data Transformation Pipelines

Chain data operations together:

```bash
# Multi-step analysis
plainspeak "load customer data, clean missing values, normalize by region, and show top spenders"

# Export pipeline results
plainspeak "analyze monthly sales trends and export results as both CSV and interactive chart"
```

## Performance Optimization

### Local vs. Remote LLM

Control when to use local or remote inference:

```bash
# Force local processing for privacy
plainspeak --local "analyze my personal finance data"

# Use remote LLM for complex queries
plainspeak --remote "explain in detail how quantum computing works"
```

### Model Configuration

Fine-tune LLM parameters for optimal performance:

```bash
# Adjust context length for complex tasks
plainspeak --context-length 4096 "summarize this long document"

# Control temperature for more deterministic results
plainspeak --temperature 0.2 "generate SQL for customer analysis"
```

## Scripting and Automation

### PlainSpeak in Shell Scripts

Incorporate PlainSpeak into your shell scripts:

```bash
#!/bin/bash
# Example: Automated log processing script
LOG_DATE=$(date -d "yesterday" +%Y-%m-%d)
plainspeak --output json "extract error counts from logs dated $LOG_DATE" > daily_report.json
```

### Scheduled Commands

Set up recurring PlainSpeak tasks:

```bash
# Create a cron-compatible command
plainspeak cron "daily at 8am: generate system health report and email to admin@example.com"

# List scheduled commands
plainspeak cron list

# Remove a scheduled command
plainspeak cron remove 3
```

### Batch Processing

Process multiple commands efficiently:

```bash
# Create a batch file (commands.txt)
# find all logs from yesterday
# extract error messages
# generate summary report
# email report to admin@example.com

# Run the batch file
plainspeak batch commands.txt
```

## Debugging and Troubleshooting

### Verbose Mode

Get detailed information about command processing:

```bash
# Show complete command processing details
plainspeak --verbose "complex query with multiple steps"
```

### Command Explanation

Have PlainSpeak explain its reasoning:

```bash
# Ask for explanation of the generated command
plainspeak --explain "find recently modified files"
```

### Safe Mode

Run with additional safeguards:

```bash
# Run in safe mode with explicit confirmations
plainspeak --safe-mode "bulk operation that affects many files"
```

## Plugin Development

### Plugin Testing

Test your custom plugins thoroughly:

```bash
# Test plugin with sample inputs
plainspeak test-plugin my-custom-plugin "sample command 1" "sample command 2"

# Run comprehensive plugin test suite
plainspeak test-plugin my-custom-plugin --test-suite ~/plugins/tests/
```

### Plugin Debugging

Debug plugin issues efficiently:

```bash
# Enable plugin debug logs
plainspeak --plugin-debug my-custom-plugin "command to test"

# Verify plugin verb recognition
plainspeak --plugin-trace "command using custom verbs"
```

## System Integration

### API Usage

Use PlainSpeak programmatically through its API:

```python
from plainspeak import PlainSpeak

ps = PlainSpeak()
result = ps.execute("find large log files and compress them")
print(result.command)  # Show the generated command
print(result.output)   # Show the command output
```

### Custom Output Formats

Get results in various formats for integration with other tools:

```bash
# Get JSON output
plainspeak --output json "find files modified today" > today_files.json

# Get CSV output for data commands
plainspeak --output csv "list processes using more than 500MB memory" > high_mem_processes.csv
```

---

Remember that PlainSpeak is designed to learn from your usage patterns. The more you use it, the better it becomes at understanding your specific needs and vocabulary. Providing feedback on command translations is valuable for improving its performance over time.
