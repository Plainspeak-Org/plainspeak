.. PlainSpeak documentation master file

PlainSpeak: The Universal Language of Computing
==============================================

*"The most profound technologies are those that disappear. They weave themselves into the fabric of everyday life until they are indistinguishable from it."* — Mark Weiser, 1991

PlainSpeak transforms everyday language into precise computer operations—allowing anyone to "speak" to their machine without learning arcane syntax, memorizing flags, or writing code. It is:

- A **Python library** that developers can embed in any application
- A **command-line tool** that turns natural requests into terminal commands and API calls
- An **extensible platform** for connecting human intent to digital action
- A **learning system** that improves through collective usage patterns

At its core, PlainSpeak is the missing translation layer between human thought and machine execution—the interface that should have always existed.

.. image:: https://img.shields.io/pypi/v/plainspeak.svg
   :target: https://pypi.org/project/plainspeak/
   :alt: PyPI version

.. image:: https://img.shields.io/github/license/cschanhniem/plainspeak.svg
   :target: https://github.com/cschanhniem/plainspeak/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/github/stars/cschanhniem/plainspeak.svg
   :target: https://github.com/cschanhniem/plainspeak/stargazers
   :alt: GitHub stars

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   user/installation
   user/getting_started
   user/guides
   user/plugins
   user/faq

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   dev/architecture
   dev/api
   dev/plugins
   dev/contributing
   dev/roadmap

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   release/distribution
   legal/license

Features
--------

- **Natural Language Interface**: Translate plain English into terminal commands, API calls, and more
- **Local Processing**: All language processing happens on your device for privacy and speed
- **Extensible Plugin System**: Add new capabilities through a simple plugin architecture
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Learning System**: Improves over time based on usage patterns
- **DataSpeak Integration**: Query and analyze data using natural language (coming soon)

Quick Start
----------

.. code-block:: bash

   # Install PlainSpeak
   pip install plainspeak

   # Start the interactive shell
   plainspeak shell

   # Or translate a single command
   plainspeak translate "list all files in the current directory"

Future Features
--------------

**DataSpeak Integration**

DataSpeak will allow users to:

- Query data using natural language
- Generate SQL queries from plain English
- Visualize data with simple commands
- Perform data analysis without SQL knowledge

Indices and tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
