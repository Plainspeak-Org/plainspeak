Plugins
=======

PlainSpeak's functionality is extended through plugins, which add support for specific types of commands and operations.

Built-in Plugins
--------------

PlainSpeak comes with several built-in plugins:

File Plugin
~~~~~~~~~~

The File plugin provides commands for working with files and directories:

- **find**: Find files matching specific criteria
- **list**: List files in a directory
- **create**: Create new files or directories
- **delete**: Delete files or directories
- **move**: Move or rename files
- **copy**: Copy files or directories
- **read**: Read the contents of a file
- **write**: Write content to a file
- **count**: Count files in a directory

Examples:

.. code-block:: text

   > find all Python files in the src directory
   > list files in Downloads sorted by size
   > create a new directory called "project"
   > delete all temporary files
   > move report.pdf to the Documents folder
   > copy all images from Downloads to Pictures
   > read the contents of config.json
   > write "Hello, world!" to hello.txt
   > count files in the current directory

System Plugin
~~~~~~~~~~~

The System plugin provides commands for system operations:

- **info**: Display system information
- **disk**: Show disk usage
- **memory**: Show memory usage
- **process**: List or manage processes
- **user**: User management commands
- **time**: Display or set the system time
- **shutdown**: Shutdown or restart the system

Examples:

.. code-block:: text

   > show system information
   > check disk space
   > show memory usage
   > list running processes
   > kill process 1234
   > show current user
   > display the current time
   > shutdown the system in 10 minutes

Network Plugin
~~~~~~~~~~~~

The Network plugin provides commands for network operations:

- **ping**: Ping a host
- **download**: Download a file
- **upload**: Upload a file
- **http**: Make HTTP requests
- **ip**: Show IP address information
- **port**: Check if a port is open
- **dns**: Perform DNS lookups

Examples:

.. code-block:: text

   > ping google.com
   > download file from https://example.com/file.zip
   > upload report.pdf to my server
   > make a GET request to https://api.example.com/data
   > show my IP address
   > check if port 8080 is open
   > lookup DNS for example.com

Git Plugin
~~~~~~~~

The Git plugin provides commands for working with Git repositories:

- **clone**: Clone a repository
- **status**: Show repository status
- **commit**: Commit changes
- **push**: Push changes to a remote
- **pull**: Pull changes from a remote
- **branch**: Create or manage branches
- **merge**: Merge branches

Examples:

.. code-block:: text

   > clone the repository from github.com/user/repo
   > show git status
   > commit all changes with message "Update documentation"
   > push changes to origin
   > pull latest changes from main
   > create a new branch called "feature"
   > merge feature branch into main

Installing Additional Plugins
---------------------------

You can install additional plugins in several ways:

1. **PyPI Packages**: Install plugins from PyPI using pip:

   .. code-block:: bash

      pip install plainspeak-plugin-name

2. **Local Plugins**: Place plugin files in the plugins directory:

   .. code-block:: bash

      cp my_plugin.py ~/.config/plainspeak/plugins/

3. **Git Repositories**: Clone plugin repositories and install them:

   .. code-block:: bash

      git clone https://github.com/user/plainspeak-plugin
      cd plainspeak-plugin
      pip install -e .

Creating Your Own Plugins
-----------------------

See the :doc:`Plugin Development Guide <../dev/plugins>` for information on creating your own plugins.
