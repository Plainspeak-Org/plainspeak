# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import glob
import importlib
from pathlib import Path

block_cipher = None

# Helper function to gather all plugin modules for hiddenimports
def collect_plugin_modules():
    plugin_dir = os.path.join('plainspeak', 'plugins')
    plugin_modules = []
    # Collect core plugin modules
    for py_file in glob.glob(os.path.join(plugin_dir, '*.py')):
        if os.path.basename(py_file) != '__init__.py':
            module_name = f"plainspeak.plugins.{os.path.basename(py_file)[:-3]}"
            plugin_modules.append(module_name)

    # Also collect subpackages
    for dir_path in glob.glob(os.path.join(plugin_dir, '*')):
        if os.path.isdir(dir_path) and os.path.exists(os.path.join(dir_path, '__init__.py')):
            subpackage = os.path.basename(dir_path)
            plugin_modules.append(f"plainspeak.plugins.{subpackage}")
            # Also add modules within the subpackage
            for sub_py_file in glob.glob(os.path.join(dir_path, '*.py')):
                if os.path.basename(sub_py_file) != '__init__.py':
                    module_name = f"plainspeak.plugins.{subpackage}.{os.path.basename(sub_py_file)[:-3]}"
                    plugin_modules.append(module_name)

    return plugin_modules

# Add all data files
def collect_data_files():
    data_files = []

    # Add translations
    trans_dir = os.path.join('plainspeak', 'translations')
    if os.path.exists(trans_dir):
        for root, dirs, files in os.walk(trans_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    rel_dir = os.path.relpath(root, '.')
                    data_files.append((file_path, rel_dir))

    # Add prompts
    prompts_dir = os.path.join('plainspeak', 'prompts')
    if os.path.exists(prompts_dir):
        for root, dirs, files in os.walk(prompts_dir):
            for file in files:
                if file.endswith(('.txt', '.md', '.json')):
                    file_path = os.path.join(root, file)
                    rel_dir = os.path.relpath(root, '.')
                    data_files.append((file_path, rel_dir))

    # Add plugin manifests
    plugins_dir = os.path.join('plainspeak', 'plugins')
    if os.path.exists(plugins_dir):
        for manifest in glob.glob(os.path.join(plugins_dir, '*.yaml')):
            data_files.append((manifest, os.path.dirname(manifest)))

    # Add demo data if exists
    demo_dir = os.path.join('plainspeak', 'data', 'demo')
    if os.path.exists(demo_dir):
        for root, dirs, files in os.walk(demo_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, '.')
                data_files.append((file_path, rel_dir))

    return data_files

# Platform-specific settings and binaries
def get_platform_settings():
    """Get platform-specific settings for the PyInstaller build."""
    settings = {
        'icon_file': None,
        'console': True,
        'name': 'plainspeak',
        'binaries': [],
        'version': '0.1.0',
        'additional_args': {}
    }

    if sys.platform.startswith('win'):
        # Windows settings
        settings['icon_file'] = os.path.join('assets', 'icons', 'windows', 'plainspeak.ico')
        settings['console'] = True
        settings['name'] = 'plainspeak'

        # Windows-specific binary dependencies
        try:
            # Include SQLite DLL
            import sqlite3
            sqlite3_dll = os.path.join(os.path.dirname(sqlite3.__file__), 'sqlite3.dll')
            if os.path.exists(sqlite3_dll):
                settings['binaries'].append((sqlite3_dll, '.'))

            # Include SSE4 compatible libraries for newer CPUs
            try:
                import numpy
                numpy_libs = os.path.join(os.path.dirname(numpy.__file__), '.libs')
                if os.path.exists(numpy_libs):
                    for lib in glob.glob(os.path.join(numpy_libs, '*.dll')):
                        settings['binaries'].append((lib, '.'))
            except ImportError:
                pass

            # Include OpenSSL DLLs
            try:
                import requests
                site_packages = os.path.dirname(os.path.dirname(requests.__file__))
                for dll in glob.glob(os.path.join(site_packages, '*.dll')):
                    if 'ssl' in os.path.basename(dll).lower() or 'crypto' in os.path.basename(dll).lower():
                        settings['binaries'].append((dll, '.'))
            except ImportError:
                pass

        except ImportError:
            pass

    elif sys.platform.startswith('darwin'):
        # macOS settings
        settings['icon_file'] = os.path.join('assets', 'icons', 'source', 'plainspeak.icns')
        settings['console'] = False
        settings['name'] = 'PlainSpeak'

        # macOS-specific framework dependencies
        try:
            # Include dylibs if needed
            import ctypes
            dylib_path = os.path.dirname(ctypes.__file__)
            if os.path.exists(dylib_path):
                for dylib in glob.glob(os.path.join(dylib_path, '*.dylib')):
                    settings['binaries'].append((dylib, '.'))
        except ImportError:
            pass

        # macOS app bundle settings
        settings['additional_args'] = {
            'info_plist': {
                'NSHighResolutionCapable': 'True',
                'LSBackgroundOnly': 'False',
                'CFBundleShortVersionString': settings['version'],
                'CFBundleVersion': settings['version'],
                'NSHumanReadableCopyright': '© 2024 PlainSpeak Organization',
                'LSEnvironment': {
                    'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
                },
                'CFBundleDisplayName': 'PlainSpeak',
                'CFBundleName': 'PlainSpeak',
                'NSPrincipalClass': 'NSApplication',
                'NSAppleScriptEnabled': False,
                'NSAppleEventsUsageDescription': 'PlainSpeak needs access to send AppleEvents to execute natural language commands.',
                'ITSAppUsesNonExemptEncryption': False,
                'CFBundleDocumentTypes': [
                    {
                        'CFBundleTypeName': 'PlainSpeak Command',
                        'CFBundleTypeExtensions': ['pscmd'],
                        'CFBundleTypeRole': 'Editor',
                    }
                ],
                'CFBundleURLTypes': [
                    {
                        'CFBundleURLName': 'org.plainspeak.url',
                        'CFBundleURLSchemes': ['plainspeak']
                    }
                ]
            }
        }

    else:  # Linux
        # Linux settings
        settings['icon_file'] = os.path.join('assets', 'icons', 'source', 'plainspeak.png')
        settings['console'] = True
        settings['name'] = 'plainspeak'

        # Linux-specific shared library dependencies
        try:
            # Include NumPy and other shared libraries if needed
            import numpy
            numpy_libs = os.path.join(os.path.dirname(numpy.__file__), '.libs')
            if os.path.exists(numpy_libs):
                for lib in glob.glob(os.path.join(numpy_libs, '*.so*')):
                    settings['binaries'].append((lib, '.'))

            # Include SSL shared libraries
            try:
                import ssl
                openssl_path = os.path.dirname(ssl.__file__)
                for lib in glob.glob(os.path.join(openssl_path, '*.so*')):
                    settings['binaries'].append((lib, '.'))
            except ImportError:
                pass

        except ImportError:
            pass

    return settings

# Get platform-specific settings
platform_settings = get_platform_settings()

# Collect data files and plugin modules
data_files = collect_data_files()
plugin_modules = collect_plugin_modules()

# Collect hidden imports
core_modules = [
    'plainspeak.core.i18n',
    'plainspeak.core.llm',
    'plainspeak.core.config',
    'plainspeak.core.utils',
    'jinja2',
    'pydantic',
    'yaml',
    'sqlite3',
    'pandas',
    'certifi',
    'urllib3',
    'requests',
    'difflib',
    'json',
    'datetime',
    'pathlib',
    'logging.handlers',
    'importlib.metadata',
    'configparser',
    'argparse',
    'shlex',
    'tempfile',
    'typing_extensions',
    'typing_inspect'
]

# Add common UI modules
ui_modules = []
if hasattr(sys, 'frozen'):
    # Only add Rich if we're building a binary (not during analysis)
    ui_modules = [
        'rich',
        'rich.console',
        'rich.syntax',
        'rich.traceback',
        'rich.logging',
        'rich.prompt',
        'rich.progress',
        'rich.panel',
        'rich.table'
    ]

a = Analysis(
    ['plainspeak/cli.py'],
    pathex=[],
    binaries=platform_settings['binaries'],
    datas=[
        ('plainspeak/plugins', 'plainspeak/plugins'),
        ('plainspeak/prompts', 'plainspeak/prompts'),
        ('plainspeak/translations', 'plainspeak/translations')
    ] + data_files,
    hiddenimports=plugin_modules + core_modules + ui_modules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PySide2', 'PyQt5'],  # Exclude unnecessary large packages
    noarchive=False,
    optimize=1,  # Optimize bytecode
)

# Filter out duplicate files
unique_datas = {}
for src, dst in a.datas:
    unique_datas[dst] = src
a.datas = [(v, k) for k, v in unique_datas.items()]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],  # Don't embed binaries in exe for faster startup
    exclude_binaries=True,
    name=platform_settings['name'],
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=platform_settings['console'],
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file='installers/macos/entitlements.plist' if sys.platform.startswith('darwin') else None,
    icon=platform_settings['icon_file'] if platform_settings['icon_file'] and os.path.exists(platform_settings['icon_file']) else None,
)

# Create a directory containing all files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=platform_settings['name'],
)

# macOS specific packaging
if sys.platform.startswith('darwin'):
    app = BUNDLE(
        coll,
        name='PlainSpeak.app',
        icon=platform_settings['icon_file'] if platform_settings['icon_file'] and os.path.exists(platform_settings['icon_file']) else None,
        bundle_identifier='org.plainspeak.app',
        info_plist=platform_settings['additional_args']['info_plist']
    )
