# File Plugin

The File Plugin provides essential file system operations, allowing you to manage files and directories through natural language commands.

## Overview

Files and directories are the foundation of any computing system. The File Plugin gives you the power to navigate, search, and manipulate your file system using simple, natural language commands.

## Verbs

| Verb | Aliases | Description |
|------|---------|-------------|
| `list` | `ls`, `dir` | List files and directories |
| `find` | `search` | Search for files matching criteria |
| `copy` | `cp` | Copy files or directories |
| `move` | `mv` | Move or rename files or directories |
| `delete` | `rm`, `remove` | Delete files or directories |
| `read` | `cat` | Display file contents |
| `create` | `touch` | Create a new file |
| `zip` | `compress` | Compress files into an archive |
| `unzip` | `extract` | Extract files from an archive |

## Usage Examples

### Listing Files

```
# Basic directory listing
list files in the downloads folder
ls ~/Downloads

# Show hidden files
list all files in my home directory including hidden ones
ls -la ~

# List with specific details
list files in documents sorted by size
ls -lS ~/Documents
```

### Finding Files

```
# Find by name
find all pdf files in my documents folder
find ~/Documents -name "*.pdf"

# Find by time
find files modified in the last 3 days
find . -type f -mtime -3

# Find large files
find files larger than 100MB in my home directory
find ~ -type f -size +100M
```

### Copying Files

```
# Copy a single file
copy report.pdf to the presentations folder
cp report.pdf presentations/

# Copy multiple files
copy all jpeg files from downloads to pictures
cp ~/Downloads/*.jpeg ~/Pictures/

# Recursive copy (directories)
copy the project folder to the backup directory
cp -r project/ backup/
```

### Moving Files

```
# Move a file
move presentation.pptx to the meeting folder
mv presentation.pptx meeting/

# Rename a file
rename old_name.txt to new_name.txt
mv old_name.txt new_name.txt

# Move multiple files
move all txt files to the documents folder
mv *.txt ~/Documents/
```

### Deleting Files

```
# Delete a file
delete temp.txt
rm temp.txt

# Delete a directory
delete the old_backups directory and all its contents
rm -r old_backups/

# Force delete without confirmation
force delete all log files
rm -f *.log
```

### Reading Files

```
# View file contents
read config.json
cat config.json

# View the beginning of a file
show the first 20 lines of log.txt
head -n 20 log.txt

# View the end of a file
show the last 50 lines of the error log
tail -n 50 error.log
```

### Creating Files

```
# Create an empty file
create a new file called notes.txt
touch notes.txt

# Create with content
create a file readme.md with "# Project Documentation" as content
echo "# Project Documentation" > readme.md
```

### Compressing Files

```
# Create a zip archive
zip the project directory into project.zip
zip -r project.zip project/

# Create a tar.gz archive
compress the logs folder into logs.tar.gz
tar -czf logs.tar.gz logs/
```

### Extracting Archives

```
# Extract a zip archive
extract archive.zip to the temp directory
unzip archive.zip -d temp/

# Extract a tar.gz archive
unzip logs.tar.gz to the backup folder
tar -xzf logs.tar.gz -C backup/
```

## Advanced Usage

### Combining with Pipes

The File Plugin works well with pipes, allowing you to combine commands:

```
# Find and delete
find all temporary files and delete them
find /tmp -name "*.tmp" -exec rm {} \;

# List, sort, and save
list all files in the project, sort by size, and save to a report
ls -lS project/ > size_report.txt
```

### Using with Variables

You can use variables in your commands:

```
# Using date variables
create a backup of my documents with today's date
tar -czf "backup_$(date +%Y-%m-%d).tar.gz" ~/Documents/
```

## Configuration

The File Plugin can be configured in your PlainSpeak configuration file:

```toml
[plugins.file]
# Default location for file operations when not specified
default_path = "~/Documents"

# Default options for listing files
list_show_hidden = false
list_long_format = true

# Safety options
allow_delete_system = false       # Prevent deletion of system directories
confirm_recursive_delete = true   # Ask for confirmation on recursive deletes
```

## Best Practices

1. **Use specific paths**: Always specify the exact path when possible to avoid operating on the wrong files.
2. **Be careful with wildcards**: Commands like `delete all files` can be dangerous. Be specific about what you want to delete.
3. **Use confirmation flags**: For destructive operations, add confirmation to avoid accidents (e.g., `delete with confirmation`).
4. **Backup before bulk operations**: Before large move/delete operations, consider creating a backup.
5. **Quote filenames with spaces**: When specifying filenames with spaces, use quotes: `copy "My Document.docx" to backup/`.

## Troubleshooting

### Common Issues

1. **Permission denied**: You might not have the necessary permissions to access certain files or directories. Use `sudo` if appropriate, or check file permissions.
2. **File not found**: Double-check that the specified path exists and is accessible.
3. **Disk space issues**: Ensure you have enough space when copying or extracting large files.
4. **Hidden files not showing**: Use the `show_hidden` parameter to view hidden files (those starting with a dot).

### Error Messages

| Error Message | Possible Solution |
|---------------|-------------------|
| "No such file or directory" | Check if the file exists or if you have a typo in the path |
| "Permission denied" | Check file permissions, or try with elevated privileges |
| "Directory not empty" | Use recursive flag for non-empty directories |
| "No space left on device" | Free up disk space or use another storage location |
