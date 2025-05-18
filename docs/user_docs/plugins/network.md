# Network Plugin

The Network Plugin provides essential networking operations, allowing you to diagnose network issues, make HTTP requests, and manage network connections through natural language commands.

## Overview

In our interconnected world, network operations are fundamental. The Network Plugin gives you tools to test connectivity, download files, connect to remote servers, and diagnose network problems with intuitive commands.

## Verbs

| Verb | Aliases | Description |
|------|---------|-------------|
| `ping` | `check` | Test connectivity to a host |
| `curl` | `http`, `request` | Make HTTP requests |
| `wget` | `download` | Download files from the web |
| `ifconfig` | `ip`, `interfaces` | Display network interfaces |
| `netstat` | `connections` | Show network connections |
| `ssh` | `connect` | Connect to remote servers |
| `scp` | `secure-copy` | Securely copy files to/from remote servers |
| `nslookup` | `dig`, `dns` | Perform DNS lookups |
| `traceroute` | `trace` | Trace the route to a host |

## Usage Examples

### Testing Connectivity

```
# Basic ping
ping google.com
ping google.com

# Limited ping count
ping google.com 5 times
ping -c 5 google.com

# Check if a server is reachable
check if example.com is online
ping -c 1 example.com
```

### Making HTTP Requests

```
# Basic GET request
curl https://api.example.com
curl https://api.example.com

# POST request with data
send a POST request to https://api.example.com/users with data "name=John&email=john@example.com"
curl -X POST -d 'name=John&email=john@example.com' https://api.example.com/users

# Request with headers
make a request to https://api.example.com with header "Authorization: Bearer token123"
curl -H 'Authorization: Bearer token123' https://api.example.com

# Save response to file
download API response from https://api.example.com to results.json
curl -o results.json https://api.example.com
```

### Downloading Files

```
# Basic download
download https://example.com/file.zip
wget https://example.com/file.zip

# Download with custom filename
download https://example.com/document.pdf as my-document.pdf
wget -O my-document.pdf https://example.com/document.pdf
```

### Network Interfaces

```
# Show all interfaces
show my network interfaces
ip addr show

# Show specific interface
show information for eth0
ifconfig eth0

# Check IP address
what is my IP address
ip addr show | grep "inet "
```

### Network Connections

```
# Show all connections
show all network connections
netstat -a

# Show only listening ports
show listening network ports
netstat -l

# Show programs using network
show which programs are using the network
netstat -tupl
```

### Remote Connections

```
# Basic SSH connection
connect to server.example.com
ssh server.example.com

# SSH with username
ssh to user@server.example.com
ssh user@server.example.com

# SSH with port and key
connect to server.example.com as user on port 2222 using key.pem
ssh -p 2222 -i key.pem user@server.example.com
```

### File Transfers

```
# Copy local file to remote server
copy myfile.txt to user@server.example.com:~/
scp myfile.txt user@server.example.com:~/

# Copy remote file to local system
download file.txt from user@server.example.com:~/
scp user@server.example.com:~/file.txt .

# Copy entire directory
copy my-project directory to server.example.com
scp -r my-project user@server.example.com:~/
```

### DNS Operations

```
# Basic DNS lookup
lookup DNS for google.com
nslookup google.com

# Specific record type
find MX records for example.com
dig MX example.com

# Reverse DNS lookup
find hostname for IP 8.8.8.8
nslookup 8.8.8.8
```

### Network Tracing

```
# Trace route to host
trace route to google.com
traceroute google.com

# Analyze network path
show the network path to example.com
traceroute example.com
```

## Advanced Usage

### Network Diagnostics

```
# Full network diagnostics
run a network diagnostic for google.com
ping -c 3 google.com && traceroute google.com && dig google.com

# Check if port is open
check if port 22 is open on server.example.com
nc -zv server.example.com 22
```

### Custom User Agents

```
# Set custom user agent
curl website.com with user agent "Mozilla/5.0"
curl -A "Mozilla/5.0" website.com
```

### HTTPS Verification

```
# Ignore HTTPS certificate verification
download from https://self-signed.example.com without certificate validation
wget --no-check-certificate https://self-signed.example.com
```

## Configuration

The Network Plugin can be configured in your PlainSpeak configuration file:

```toml
[plugins.network]
# Default options
ping_count = 5
download_directory = "~/Downloads"
default_ssh_user = "username"
default_ssh_key = "~/.ssh/id_rsa"

# Timeout settings
request_timeout = 30          # Seconds for HTTP requests
connection_timeout = 10       # Seconds for connection attempts

# Security settings
verify_ssl = true             # Verify SSL certificates by default
```

## Best Practices

1. **Be mindful of bandwidth**: Large downloads can consume significant bandwidth, especially on metered connections.
2. **Secure your credentials**: Avoid using plaintext passwords in SSH commands; prefer key-based authentication.
3. **Respect rate limits**: When making API requests, be considerate of rate limits to avoid being blocked.
4. **Check before you trace**: Traceroute and network scanning tools should be used responsibly and not against networks without permission.
5. **Save large outputs**: For commands that generate large outputs, consider saving to a file for easier analysis.

## Troubleshooting

### Common Issues

1. **Connection timeout**: The remote host may be down or blocked by a firewall.
2. **Name resolution failed**: DNS issues; check if the domain name is correct and your DNS server is working.
3. **Permission denied**: SSH connections might require the correct key or credentials.
4. **Certificate errors**: SSL certificate issues when connecting to HTTPS sites can be caused by expired or invalid certificates.

### Error Messages

| Error Message | Possible Solution |
|---------------|-------------------|
| "Connection refused" | The service might not be running or is blocked by a firewall |
| "No route to host" | Network routing issue or the host is down |
| "Name or service not known" | DNS resolution failed; check the hostname or DNS settings |
| "Operation timed out" | Increase timeout values or check network connectivity |
| "Certificate verification failed" | Use `--no-check-certificate` option (only when you trust the source) |
