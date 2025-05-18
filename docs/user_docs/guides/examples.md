# PlainSpeak by Example

This guide provides examples of natural language commands you can use with PlainSpeak, showing the power of using everyday language to interact with your computer.

## Basic File Operations

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Show me all the PDF files in my downloads folder" | List all PDF files in your Downloads directory |
| "Find large files over 1GB that I haven't accessed in the last year" | Search for files >1GB with access time >1 year ago |
| "Create a new folder called project-docs" | Make a new directory named "project-docs" |
| "Move all the screenshots from my desktop to a folder called 'screenshots'" | Move screen capture files from Desktop to a screenshots folder |
| "Delete all temporary files in the downloads folder" | Remove files with temp/tmp extensions from Downloads |

## Text and Content Processing

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Find all mentions of 'critical bug' in the log files" | Search log files for the phrase "critical bug" |
| "Count how many lines are in this code file" | Count lines in the current file |
| "Extract all email addresses from this text file" | Use regex to find email patterns in the specified file |
| "Find and replace 'old function name' with 'new function name' in all python files" | Perform a find/replace across .py files |
| "Summarize the contents of this log file" | Extract and display important patterns from a log file |

## System Information and Management

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Show me which processes are using the most memory" | Run a command to display processes sorted by memory usage |
| "What's my IP address?" | Display your local and public IP addresses |
| "How much disk space do I have left?" | Show available storage on all drives |
| "Check if port 8080 is in use" | Check for processes using that port |
| "Monitor CPU usage for the next 5 minutes" | Start a CPU usage monitoring tool |

## Development and Programming

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Set up a new Python virtual environment here" | Create and activate a venv in the current directory |
| "Start a development server on port 3000" | Run an appropriate dev server command |
| "Show me all TODO comments in the codebase" | Find and list all TODO markers in code files |
| "Create a new git branch called feature-login and switch to it" | Execute git commands to create and checkout a new branch |
| "Run the tests for the authentication module" | Execute test command for the specified module |

## Networking and Internet

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Download the latest release of TensorFlow" | Fetch the latest TensorFlow package |
| "What's the latency to google.com?" | Run ping or similar network diagnostic |
| "Check if my website is up" | Perform an HTTP request to verify site status |
| "Show me all devices on my network" | Run a network scan command |
| "Start a simple web server in this folder" | Start a basic HTTP server in the current directory |

## Data Processing

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Convert this CSV file to JSON" | Transform the file format using appropriate tools |
| "Summarize the columns in this dataset" | Display column statistics for a data file |
| "Extract the third column from this CSV file" | Use tools like awk/cut to extract column data |
| "Find duplicate entries in this data file" | Process the file to identify duplicates |
| "Plot a histogram of the ages column" | Generate a visualization using available tools |

## Content Creation and Media

| Natural Language Command | What PlainSpeak Will Do |
|--------------------------|-------------------------|
| "Resize all images in this folder to 800x600" | Use image processing tools for batch resizing |
| "Convert this video to mp4 format" | Run appropriate video conversion tools |
| "Extract the audio from this video file" | Separate the audio track from a video |
| "Create a contact sheet from these photos" | Generate a visual index of images |
| "Add a watermark to all these images" | Apply text/image watermarks to a set of files |

## Advanced Usage Patterns

### Command Chaining

You can combine multiple operations in a single command:

"Find all PDF files in my documents folder, then compress them into an archive called 'all-documents.zip'"

### Using Variables and References

PlainSpeak maintains context across commands:

```
> Find all python files modified in the last week
Found 7 files matching your criteria.

> Count the lines of code in those files
Analyzing 7 files from previous result...
Total: 1,243 lines of code
```

### Workflows and Scheduling

You can create scheduled or triggered actions:

"Every Friday at 5pm, back up my project folder to Dropbox and send me an email confirmation"

## Customizing Commands

If PlainSpeak generates a command that's not quite what you want, you can:

1. Edit the command before execution when prompted
2. Cancel the operation
3. Ask PlainSpeak to try again with more specific instructions

Example:

```
> Find large files on my system
I'll search for files larger than 100MB. Here's the command I'll run:
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -rh

[E]dit, [C]ancel, or [R]un this command: E

Edit command> find /home/user -type f -size +500M -exec ls -lh {} \; 2>/dev/null | sort -rh

Running your edited command...
```

## Next Steps

- Explore [PlainSpeak plugins](../plugins/overview.md) to extend capabilities
- Learn [how PlainSpeak works](how_it_works.md) under the hood
- Check out the [troubleshooting guide](../faq/troubleshooting.md) for common issues
