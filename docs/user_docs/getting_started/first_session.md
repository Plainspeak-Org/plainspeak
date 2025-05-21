# Your First PlainSpeak Session

This guide will walk you through your first session with PlainSpeak, helping you understand how to interact with the system and make the most of its natural language capabilities.

## Starting PlainSpeak

After [installing PlainSpeak](../installation/index.md), you can start the interactive shell:

```bash
plainspeak shell
```

You should see a welcome message and a prompt:

```
PlainSpeak 1.0  •  Your natural gateway to computing power

>
```

The `>` symbol is where you'll type your natural language commands.

## Command Options

PlainSpeak offers multiple ways to interact with it:

### 1. Interactive Shell

```bash
plainspeak shell
```

This starts an interactive session where you can type commands directly.

### 2. Direct Translation

You can use PlainSpeak directly without entering the shell:

```bash
# Traditional syntax with the translate verb
plainspeak translate "list files in the current directory"

# Simplified syntax without the translate verb
plainspeak "list files in the current directory"
```

### 3. Conversational Alias

For an even more natural experience, you can use the `pls` alias:

```bash
pls "convert all CSV files to JSON format"
```

The `pls` command functions exactly like `plainspeak` but offers a more conversational experience that aligns with everyday language.

## Basic Commands

Let's start with some simple commands to get a feel for how PlainSpeak works:

### Listing Files

Try asking PlainSpeak to list files in your current directory:

```
> list files in the current directory
```

Or if you're using the direct command approach:

```bash
pls "list files in the current directory"
```

PlainSpeak will translate this to a shell command, show it to you, and ask for confirmation:

```
Translated ⤵
$ ls -la
Run it? [Y/n]
```

Press `Y` (or Enter) to execute the command, or `n` to cancel.

### Finding Files

You can ask PlainSpeak to find specific files:

```
> find all PDF files in my Documents folder
```

Or using the direct command:

```bash
pls "find all PDF files in my Documents folder"
```

PlainSpeak might translate this as:

```
Translated ⤵
$ find ~/Documents -type f -name "*.pdf"
Run it? [Y/n]
```

### Creating and Editing Files

You can create and edit files:

```
> create a new file called todo.txt with a list of tasks
```

PlainSpeak might suggest:

```
Translated ⤵
$ cat > todo.txt << EOF
# My Todo List

- Task 1
- Task 2
- Task 3
EOF
Run it? [Y/n]
```

## Understanding the Translation Process

PlainSpeak translates your natural language into shell commands using these steps:

1. **Input**: You provide a natural language command
2. **Translation**: PlainSpeak uses a local LLM to understand your intent
3. **Verification**: PlainSpeak shows you the translated command
4. **Execution**: After your approval, the command is executed
5. **Learning**: PlainSpeak learns from your feedback to improve future translations

## Working with Plugins

PlainSpeak comes with several built-in plugins for different tasks. You can list available plugins:

```
> plugins
```

This will show you all available plugins and their verbs:

```
Available Plugins:

file: File operations like listing, copying, moving, etc.
  Supported verbs:
  list, ls, dir, find, search
  copy, cp, move, mv, delete
  rm, remove, read, cat, create
  touch, zip, compress, unzip, extract

system: System operations like checking processes, disk usage, etc.
  Supported verbs:
  ps, processes, kill, terminate, df
  disk, du, size, free, memory
  top, monitor, uname, system, date
  time, uptime, hostname

network: Network operations like ping, curl, wget, etc.
  ...

text: Text operations like grep, sed, awk, etc.
  ...
```

### Plugin Examples

Here are some examples of using different plugins:

#### System Plugin

```
> show me the top 5 CPU-intensive processes
```

```
Translated ⤵
$ ps aux --sort=-%cpu | head -n 6
Run it? [Y/n]
```

#### Network Plugin

```
> check if google.com is reachable
```

```
Translated ⤵
$ ping -c 4 google.com
Run it? [Y/n]
```

## Editing Commands

If PlainSpeak doesn't translate your request exactly as you want, you can edit the command before execution:

```
> find large files in my home directory
```

```
Translated ⤵
$ find ~/ -type f -size +100M
Run it? [Y/n/e] e
```

By typing `e`, you'll be able to edit the command:

```
Edit command: find ~/ -type f -size +100M -exec ls -lh {} \; | sort -hr
```

After editing, press Enter to execute the modified command.

## Command History

PlainSpeak keeps track of your command history. You can:

- Press the up/down arrow keys to navigate through previous commands
- Type `history` to see a list of all previous commands
- Use `!n` to repeat command number n from the history

```
> history
```

```
1: list files in the current directory
2: find all PDF files in my Documents folder
3: create a new file called todo.txt with a list of tasks
```

## Getting Help

If you need help at any time, you can:

```
> help
```

This will show you general help information. You can also get help on specific topics:

```
> help plugins
```

```
> help file plugin
```

## Advanced Usage

As you become more comfortable with PlainSpeak, you can try more complex commands:

```
> find all Python files modified in the last week, count the lines of code in each, and sort them by line count
```

```
Translated ⤵
$ find . -name "*.py" -mtime -7 -exec wc -l {} \; | sort -n
Run it? [Y/n]
```

## Exiting PlainSpeak

To exit the PlainSpeak shell:

```
> exit
```

or

```
> quit
```

## Next Steps

Now that you've completed your first session with PlainSpeak, you might want to:

- Learn more about [available plugins](../plugins/overview.md)
- Explore [example commands](../guides/examples.md) for inspiration
- Read about [how PlainSpeak works](../guides/how_it_works.md) under the hood
- Check out the [troubleshooting guide](../faq/troubleshooting.md) if you encounter any issues

Remember, the more you use PlainSpeak, the better it gets at understanding your specific needs and preferences. The system learns from your feedback and command edits to provide more accurate translations over time.
