# System Plugin

The System Plugin provides essential system operations, allowing you to monitor and manage your system resources through natural language commands.

## Overview

Managing system resources is a critical aspect of computer maintenance. The System Plugin gives you tools to check processes, monitor resource usage, and perform various system operations with simple, intuitive commands.

## Verbs

| Verb | Aliases | Description |
|------|---------|-------------|
| `ps` | `processes` | List running processes |
| `kill` | `terminate` | Terminate a process |
| `df` | `disk` | Check disk space usage |
| `du` | `size` | Check directory size |
| `free` | `memory` | Check memory usage |
| `top` | `monitor` | Monitor system resources |
| `uname` | `system` | Display system information |
| `date` | `time` | Show or set date and time |
| `uptime` | | Show how long the system has been running |
| `hostname` | | Show or set the system hostname |

## Usage Examples

### Process Management

```
# List all processes
show all running processes
ps aux

# Find specific processes
list all python processes
ps aux | grep python

# Kill a process by PID
kill process 1234
kill 1234

# Force kill an unresponsive process
force kill process 5678
kill -9 5678
```

### Disk Usage

```
# Check overall disk usage
show disk space usage
df -h

# Check specific filesystem
check space on the root partition
df -h /

# Check directory size
what's the size of my downloads folder
du -sh ~/Downloads

# Find largest directories
find the largest directories in my home folder
du -h ~ | sort -hr | head -n 10
```

### Memory Usage

```
# Check memory usage
show memory usage
free -h

# Monitor memory usage over time
monitor memory usage every 5 seconds
watch -n 5 free -h
```

### System Monitoring

```
# Monitor system resources
monitor system resources
top

# Monitor in batch mode for scripting
monitor system for 5 iterations in batch mode
top -b -n 5

# Monitor specific process
monitor cpu usage of chrome
top -p $(pgrep chrome)
```

### System Information

```
# Show all system information
what system am I running
uname -a

# Show kernel version
show kernel version
uname -r

# Show hardware information
show detailed hardware information
lshw
```

### Date and Time

```
# Show current date and time
what is the current time
date

# Show date in custom format
show date in yyyy-mm-dd format
date +'%Y-%m-%d'

# Set system time (requires permissions)
set the system time to "2023-07-31 15:30:00"
sudo date -s "2023-07-31 15:30:00"
```

### System Uptime

```
# Check how long the system has been running
how long has the system been running
uptime

# Show uptime in pretty format
show uptime in a readable format
uptime -p
```

### Hostname Management

```
# Show current hostname
what is my computer's name
hostname

# Set hostname (requires permissions)
set hostname to myserver
sudo hostname myserver
```

## Advanced Usage

### System Diagnostics

```
# Full system report
generate a system report
hostnamectl; uptime; free -h; df -h; lscpu

# Check running services
what services are running
systemctl list-units --type=service --state=running
```

### Performance Analysis

```
# CPU load
check CPU load
uptime

# IO stats
show disk IO statistics
iostat

# Network stats
show network statistics
netstat -tuln
```

### Cron Jobs and Scheduling

```
# List scheduled tasks
show my scheduled tasks
crontab -l

# View system cron jobs
show system cron jobs
ls -l /etc/cron.*
```

## Configuration

The System Plugin can be configured in your PlainSpeak configuration file:

```toml
[plugins.system]
# Default options for process listing
ps_show_all = true
ps_full_format = false

# Safety options
allow_kill_system_processes = false  # Prevent killing critical system processes
confirm_kill = true                  # Ask for confirmation before killing processes
```

## Best Practices

1. **Be careful with system changes**: Commands that modify system settings (like setting hostname or date) often require sudo privileges and can impact system operation.
2. **Use process IDs carefully**: Double-check process IDs before killing them to avoid terminating the wrong process.
3. **Monitor resource usage regularly**: Regular monitoring helps identify problems before they become critical.
4. **Use human-readable formats**: Add the "human-readable" parameter to commands like `df` and `du` for easier interpretation.
5. **Filter output for clarity**: Pipe output to `grep` to filter for specific information when dealing with large outputs.

## Troubleshooting

### Common Issues

1. **Permission denied**: Many system operations require elevated privileges. Use `sudo` when necessary.
2. **Process not found**: Ensure the process ID or name exists before attempting to kill it.
3. **Disk space warnings**: If you're running low on disk space, investigate large directories with `du` and consider cleanup.
4. **High memory usage**: If `free` shows low available memory, identify memory-hungry processes with `top`.

### Error Messages

| Error Message | Possible Solution |
|---------------|-------------------|
| "Permission denied" | Run the command with sudo or as administrator |
| "No such process" | Verify the process ID is correct and still running |
| "Operation not permitted" | Check if you have the necessary permissions for the operation |
| "Cannot find the device" | Ensure the specified device or partition exists |
