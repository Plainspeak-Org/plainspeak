Getting Started
===============

This guide will help you get started with PlainSpeak, the universal language of computing.

Basic Usage
----------

After :doc:`installing PlainSpeak <installation>`, you can start using it in several ways:

Interactive Shell
~~~~~~~~~~~~~~~

The most common way to use PlainSpeak is through its interactive shell:

.. code-block:: bash

   plainspeak shell

This will start an interactive session where you can type natural language commands:

.. code-block:: text

   PlainSpeak v0.1.0
   Type 'help' for a list of commands, 'exit' to quit.
   > list all files in the current directory

   I'll list all files in the current directory.

   Command: ls -la

   Execute? [Y/n/edit]: y

   total 56
   drwxr-xr-x  12 user  staff   384 May 17 14:22 .
   drwxr-xr-x   5 user  staff   160 May 17 13:45 ..
   -rw-r--r--   1 user  staff  1256 May 17 14:22 README.md
   drwxr-xr-x   4 user  staff   128 May 17 14:10 docs
   -rw-r--r--   1 user  staff   837 May 17 14:15 pyproject.toml
   drwxr-xr-x   8 user  staff   256 May 17 14:20 plainspeak
   drwxr-xr-x   5 user  staff   160 May 17 14:18 tests

Single Command
~~~~~~~~~~~~

You can also use PlainSpeak to translate a single command:

.. code-block:: bash

   plainspeak translate "find all Python files modified in the last week"

This will translate the command and prompt you to execute it:

.. code-block:: text

   I'll find all Python files modified in the last week.

   Command: find . -name "*.py" -mtime -7

   Execute? [Y/n/edit]:

Command Line Options
------------------

PlainSpeak provides several command line options:

.. code-block:: bash

   # Show help
   plainspeak --help

   # Show version
   plainspeak --version

   # Use a specific configuration file
   plainspeak --config /path/to/config.toml

   # Enable debug logging
   plainspeak --debug

   # List available plugins
   plainspeak plugins

Understanding the Output
---------------------

When you enter a natural language command, PlainSpeak:

1. **Interprets** your intent
2. **Translates** it to a shell command or API call
3. **Shows** you the command it will execute
4. **Asks** for confirmation before executing
5. **Displays** the result

You can:

- Press **Y** (or Enter) to execute the command
- Press **N** to cancel
- Press **E** to edit the command before executing

Configuration
-----------

PlainSpeak can be configured using a TOML file located at ``~/.config/plainspeak/config.toml``:

.. code-block:: toml

   [llm]
   model_path = "~/.config/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf"
   model_type = "llama"
   gpu_layers = 0  # Set to a higher number to use GPU acceleration

   [plugins]
   disabled = []  # List of plugins to disable
   enabled_only = false  # When true, only explicitly enabled plugins are loaded
   directory = "~/.config/plainspeak/plugins"  # Custom plugin directory

   [shell]
   history_file = "~/.config/plainspeak/history.json"
   max_history = 1000
   auto_execute = false  # When true, commands are executed without confirmation

Examples
-------

Here are some examples of what you can do with PlainSpeak:

File Operations
~~~~~~~~~~~~~

.. code-block:: text

   > find large PDF files in Downloads
   > create a new directory called "project"
   > move all images from Downloads to Pictures
   > count the number of files in this directory

System Information
~~~~~~~~~~~~~~~~

.. code-block:: text

   > show system information
   > check disk space
   > list running processes
   > show memory usage

Network Operations
~~~~~~~~~~~~~~~~

.. code-block:: text

   > ping google.com
   > download file from https://example.com/file.zip
   > check if port 8080 is open
   > show my IP address

Next Steps
---------

Now that you're familiar with the basics, you can:

- Learn about :doc:`available plugins <plugins>`
- Explore the :doc:`user guides <guides>`
- Check out the :doc:`FAQ <faq>` for common questions
- Consider :doc:`creating your own plugins <../dev/plugins>`
