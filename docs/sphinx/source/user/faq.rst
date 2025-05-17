Frequently Asked Questions
=========================

General Questions
---------------

What is PlainSpeak?
~~~~~~~~~~~~~~~~~

PlainSpeak is a natural language interface for computing that translates plain English into terminal commands, API calls, and other computer operations. It allows you to interact with your computer using everyday language instead of memorizing complex syntax.

How does PlainSpeak work?
~~~~~~~~~~~~~~~~~~~~~~~

PlainSpeak uses a local large language model (LLM) to understand your intent, then maps that intent to specific commands using a plugin system. It shows you the command it's going to run and asks for your confirmation before executing it. See the :doc:`How It Works <guides/how_it_works>` guide for more details.

Is PlainSpeak free and open source?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, PlainSpeak is free and open source software, released under the MIT license. You can view the source code, contribute to the project, and use it for any purpose.

Does PlainSpeak send my commands to the cloud?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No, PlainSpeak processes all commands locally on your device. Your commands, data, and usage patterns never leave your computer. This ensures privacy and allows PlainSpeak to work offline.

Installation Questions
-------------------

What are the system requirements?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PlainSpeak requires:

- Python 3.11 or higher
- 4 GB RAM recommended (2 GB minimum)
- 500 MB disk space for the application
- 1-4 GB additional space for language models

How do I install PlainSpeak?
~~~~~~~~~~~~~~~~~~~~~~~~~

You can install PlainSpeak using pip:

.. code-block:: bash

   pip install plainspeak

See the :doc:`Installation Guide <installation>` for detailed instructions.

Why am I getting a "Model file not found" error?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This error occurs when PlainSpeak can't find the language model file. Make sure you've downloaded a compatible GGUF model and configured PlainSpeak to use it. See the :doc:`Installation Guide <installation>` for instructions.

Usage Questions
------------

How do I start using PlainSpeak?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installation, you can start the interactive shell:

.. code-block:: bash

   plainspeak shell

Then type your commands in plain English. See the :doc:`Getting Started Guide <getting_started>` for more information.

What kinds of commands can I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use PlainSpeak for a wide range of tasks, including:

- File operations (finding, copying, moving files)
- System operations (checking disk space, managing processes)
- Network operations (downloading files, making HTTP requests)
- Git operations (cloning repositories, committing changes)
- And more, depending on the plugins you have installed

Can I use PlainSpeak in scripts?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, you can use PlainSpeak in scripts by using the `translate` command:

.. code-block:: bash

   plainspeak translate "find all Python files modified today" --execute

This will translate the command and execute it without asking for confirmation.

How do I add new capabilities to PlainSpeak?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can extend PlainSpeak's capabilities by installing or creating plugins. See the :doc:`Plugins <plugins>` guide for information on available plugins and the :doc:`Plugin Development Guide <../dev/plugins>` for creating your own.

Technical Questions
----------------

How does PlainSpeak handle ambiguity?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a command is ambiguous, PlainSpeak:

1. Uses context from previous commands
2. Looks at your current directory and environment
3. Considers the most common interpretation
4. Asks for clarification if necessary

Can I use PlainSpeak with a different language model?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, you can configure PlainSpeak to use different GGUF language models. Edit your config.toml file to specify a different model path:

.. code-block:: toml

   [llm]
   model_path = "/path/to/your/model.gguf"
   model_type = "llama"  # or another model type

How can I improve performance?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To improve performance:

1. Use a smaller language model if speed is more important than accuracy
2. Enable GPU acceleration by setting `gpu_layers` in your config.toml
3. Close other resource-intensive applications
4. Use an SSD instead of an HDD for storing the model

Troubleshooting
-------------

PlainSpeak is running slowly. What can I do?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If PlainSpeak is running slowly:

1. Check if you have GPU acceleration enabled
2. Consider using a smaller language model
3. Close other resource-intensive applications
4. Make sure your system meets the recommended requirements

I'm getting incorrect commands. How can I fix this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If PlainSpeak is generating incorrect commands:

1. Be more specific in your requests
2. Edit the command before executing it (press 'e' when prompted)
3. Check if you have the appropriate plugins installed
4. Consider using a larger, more accurate language model

Where can I get help if I have more questions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have more questions:

1. Check the documentation at https://docs.plainspeak.org
2. Visit the GitHub repository at https://github.com/cschanhniem/plainspeak
3. Join the community discussions at https://github.com/cschanhniem/plainspeak/discussions
4. Report issues at https://github.com/cschanhniem/plainspeak/issues
