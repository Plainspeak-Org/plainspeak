Plugin Development
=================

This guide walks you through the process of creating custom plugins for PlainSpeak, allowing you to extend its capabilities with your own natural language commands.

Plugin Architecture Overview
--------------------------

PlainSpeak plugins connect natural language verbs to specific implementations. A plugin consists of:

1. **Metadata** - Information about your plugin including name, description, and supported verbs
2. **Templates** - Jinja2 templates that convert structured intents into concrete commands
3. **Code** (optional) - Python code for more complex operations

Simple Plugin Example: YAML-Based
--------------------------------

For straightforward command mapping, you can create a plugin using just YAML:

.. code-block:: yaml

   name: file-operations
   description: Basic file system operations
   version: 0.1.0
   author: Your Name

   verbs:
     - find
     - count

   commands:
     find:
       template: >
         find {{ path | default('.') }}
         {% if type %}
         -type {{ type }}
         {% endif %}
         {% if name %}
         -name "{{ name }}"
         {% endif %}
         {% if size %}
         -size {{ size }}
         {% endif %}
       description: "Find files matching criteria"
       examples:
         - "find large PDF files in the Documents folder"
       required_args: []
       optional_args:
         path: "."
         type: ""
         name: ""
         size: ""

     count:
       template: >
         find {{ path | default('.') }} -type f | wc -l
       description: "Count files in a directory"
       examples:
         - "count files in Downloads"
       required_args: []
       optional_args:
         path: "."

Advanced Plugin Example: Python-Based
-----------------------------------

For more complex functionality, create a Python plugin:

.. code-block:: python

   from plainspeak.plugins import Plugin, register_plugin
   from plainspeak.types import Intent, CommandResult
   import subprocess
   import json

   class GithubPlugin(Plugin):
       """Plugin for GitHub operations."""

       def __init__(self):
           super().__init__(
               name="github",
               description="GitHub operations",
               verbs=["clone", "create", "list-repos"]
           )

       def execute(self, intent: Intent) -> CommandResult:
           """Execute the GitHub command based on the intent."""
           verb = intent.verb

           if verb == "clone":
               return self._clone_repo(intent)
           elif verb == "create":
               return self._create_repo(intent)
           elif verb == "list-repos":
               return self._list_repos(intent)

           return CommandResult(
               success=False,
               output=f"Unknown verb: {verb}",
               command=f"github {verb}"
           )

       def _clone_repo(self, intent: Intent) -> CommandResult:
           """Clone a GitHub repository."""
           repo = intent.args.get("repo")
           path = intent.args.get("path", ".")

           if not repo:
               return CommandResult(
                   success=False,
                   output="Repository name is required",
                   command="git clone"
               )

           # Add github.com prefix if not present
           if not repo.startswith("https://") and not repo.startswith("git@"):
               if "/" not in repo:
                   return CommandResult(
                       success=False,
                       output="Repository should be in format 'owner/repo'",
                       command="git clone"
                   )

               repo = f"https://github.com/{repo}"

           command = f"git clone {repo} {path}"

           try:
               result = subprocess.run(
                   command,
                   shell=True,
                   check=True,
                   capture_output=True,
                   text=True
               )
               return CommandResult(
                   success=True,
                   output=result.stdout,
                   command=command
               )
           except subprocess.CalledProcessError as e:
               return CommandResult(
                   success=False,
                   output=e.stderr,
                   command=command
               )

   # Register the plugin
   register_plugin(GithubPlugin())

Plugin Installation Locations
---------------------------

PlainSpeak looks for plugins in several locations:

1. **Built-in plugins**: Included with PlainSpeak (``plainspeak/plugins/``)
2. **User plugins**: In the user plugins directory (``~/.config/plainspeak/plugins/``)
3. **Site-wide plugins**: System-wide installation location
4. **Python packages**: Installed via pip with the ``plainspeak.plugins`` entry point

Creating a Plugin Package
-----------------------

To distribute your plugin as a Python package:

1. Create a package structure:

.. code-block:: text

   my-plainspeak-plugin/
   ├── pyproject.toml
   ├── README.md
   ├── my_plugin/
   │   ├── __init__.py
   │   └── plugin.py

2. Set up ``pyproject.toml``:

.. code-block:: toml

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "plainspeak-plugin-myplugin"
   version = "0.1.0"
   description = "My custom PlainSpeak plugin"
   readme = "README.md"
   authors = [
       {name = "Your Name", email = "your.email@example.com"},
   ]
   dependencies = [
       "plainspeak>=0.1.0",
   ]

   [project.entry-points."plainspeak.plugins"]
   myplugin = "my_plugin.plugin:register"

3. Implement your plugin in ``my_plugin/plugin.py``:

.. code-block:: python

   from plainspeak.plugins import Plugin, register_plugin

   class MyPlugin(Plugin):
       # Plugin implementation
       ...

   def register():
       # This function will be called to register your plugin
       return register_plugin(MyPlugin())

Best Practices
------------

1. **Descriptive Names**: Use clear, descriptive names for your plugin and commands
2. **Comprehensive Examples**: Provide multiple examples to help users understand how to use your plugin
3. **Error Handling**: Implement robust error handling and provide helpful error messages
4. **Documentation**: Document your plugin thoroughly, including all available commands and parameters
5. **Testing**: Write tests for your plugin to ensure it works as expected
6. **Security**: Be mindful of security implications, especially when executing shell commands
