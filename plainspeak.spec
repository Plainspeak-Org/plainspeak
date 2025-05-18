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
    
    return plugin_modules

# Add translations to datas
trans_dir = os.path.join('plainspeak', 'translations')
trans_files = []
if os.path.exists(trans_dir):
    trans_files = [(os.path.join(trans_dir, f), trans_dir) for f in os.listdir(trans_dir) if f.endswith('.json')]

# Collect all prompts
prompts_dir = os.path.join('plainspeak', 'prompts')
prompts_files = []
if os.path.exists(prompts_dir):
    for root, dirs, files in os.walk(prompts_dir):
        for file in files:
            if file.endswith(('.txt', '.md', '.json')):
                file_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, '.')
                prompts_files.append((file_path, rel_dir))

# Platform-specific settings and binaries
if sys.platform.startswith('win'):
    icon_file = os.path.join('assets', 'icons', 'windows', 'plainspeak.ico')
    console = True
    name = 'plainspeak'
    add_binary_files = []
    
    # Windows-specific binary dependencies
    try:
        import sqlite3
        sqlite3_dll = os.path.join(os.path.dirname(sqlite3.__file__), 'sqlite3.dll')
        if os.path.exists(sqlite3_dll):
            add_binary_files.append((sqlite3_dll, '.'))
    except ImportError:
        pass
        
elif sys.platform.startswith('darwin'):
    icon_file = os.path.join('assets', 'icons', 'source', 'plainspeak.icns')
    console = False
    name = 'PlainSpeak'
    add_binary_files = []
    
    # macOS-specific framework dependencies
    try:
        import ctypes
        dylib_path = os.path.dirname(ctypes.__file__)
        if os.path.exists(dylib_path):
            for dylib in glob.glob(os.path.join(dylib_path, '*.dylib')):
                add_binary_files.append((dylib, '.'))
    except ImportError:
        pass
        
else:  # Linux
    icon_file = os.path.join('assets', 'icons', 'source', 'plainspeak.png')
    console = True
    name = 'plainspeak'
    add_binary_files = []
    
    # Linux-specific shared library dependencies
    try:
        import numpy
        numpy_libs = os.path.join(os.path.dirname(numpy.__file__), '.libs')
        if os.path.exists(numpy_libs):
            for lib in glob.glob(os.path.join(numpy_libs, '*.so*')):
                add_binary_files.append((lib, '.'))
    except ImportError:
        pass

# Collect hidden imports
plugin_modules = collect_plugin_modules()
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
    'urllib3'
]

a = Analysis(
    ['plainspeak/cli.py'],
    pathex=[],
    binaries=add_binary_files,
    datas=[
        ('plainspeak/plugins', 'plainspeak/plugins'),
        ('plainspeak/prompts', 'plainspeak/prompts'),
        ('plainspeak/translations', 'plainspeak/translations')
    ] + trans_files + prompts_files,
    hiddenimports=plugin_modules + core_modules,
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
    a.binaries,
    a.datas,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if os.path.exists(icon_file) else None,
)

# macOS specific packaging
if sys.platform.startswith('darwin'):
    app = BUNDLE(
        exe,
        name='PlainSpeak.app',
        icon=icon_file if os.path.exists(icon_file) else None,
        bundle_identifier='org.plainspeak.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '0.1.0',
            'CFBundleVersion': '0.1.0',
            'NSHumanReadableCopyright': '© 2024 PlainSpeak Organization',
            'LSEnvironment': {
                'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
            },
            'CFBundleDisplayName': 'PlainSpeak',
            'CFBundleName': 'PlainSpeak',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'NSAppleEventsUsageDescription': 'PlainSpeak needs access to send AppleEvents to execute natural language commands.',
            'ITSAppUsesNonExemptEncryption': False
        }
    )
