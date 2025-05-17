# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PlainSpeak"
copyright = "2025, PlainSpeak Team"
author = "PlainSpeak Team"

version = "0.1.0"  # Updated to match pyproject.toml
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx_autodoc_typehints',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # Changed to Read the Docs theme
html_static_path = ["_static"]
html_logo = "../../../assets/icons/plainspeak.png"  # Add logo if available
html_favicon = "../../../assets/icons/favicon.ico"  # Add favicon if available

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
}

# -- Additional options ------------------------------------------------------
nitpicky = True
nitpick_ignore = []
todo_include_todos = True

# -- Options for HTML context ------------------------------------------------
html_context = {
    'display_github': True,
    'github_user': 'cschanhniem',
    'github_repo': 'plainspeak',
    'github_version': 'main',
    'conf_py_path': '/docs/sphinx/source/',
}
