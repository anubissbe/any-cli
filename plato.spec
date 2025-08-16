# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Define data files and hidden imports
block_cipher = None

# Hidden imports for dependencies that PyInstaller might miss
hidden_imports = [
    'plato',
    'plato.cli',
    'plato.interactive_cli',
    'plato.core',
    'plato.core.ai_router',
    'plato.core.context_manager',
    'plato.core.mcp_manager',
    'plato.server',
    'plato.server.api',
    'plato.integrations',
    'plato.integrations.serena_mcp',
    'asyncio',
    'httpx',
    'typer',
    'rich',
    'rich.console',
    'rich.panel',
    'rich.table',
    'rich.progress',
    'rich.layout',
    'rich.live',
    'rich.markdown',
    'rich.syntax',
    'rich.text',
    'rich.tree',
    'rich.align',
    'rich.prompt',
    'fastapi',
    'uvicorn',
    'websockets',
    'pydantic',
    'pydantic_settings',
    'python_json_logger',
    'aiofiles',
    'tenacity',
    'openai',
    'anthropic',
    'google.generativeai',
    'tiktoken',
    'colorama',
    'pathlib',
    'json',
    'os',
    'sys',
    'time',
    'datetime',
    'traceback',
    'subprocess',
    'enum',
    'typing',
    'dataclasses',
    'collections',
    'functools',
    'itertools',
    'concurrent.futures',
    'threading',
    'multiprocessing',
    'signal',
    'argparse',
]

# Optional imports that might not be available
optional_imports = [
    'git',
    'gitpython',
    'pygments',
    'pygments.lexers',
    'pygments.util',
    'mcp',
]

# Add optional imports if available
for module in optional_imports:
    try:
        __import__(module)
        hidden_imports.append(module)
    except ImportError:
        pass

# Data files to include
datas = [
    ('plato/', 'plato/'),
    ('config.yaml', '.'),
    ('config.example.yaml', '.'),
]

# Add any additional data files if they exist
additional_files = [
    'README.md',
    'pyproject.toml',
]

for file_path in additional_files:
    if Path(file_path).exists():
        datas.append((file_path, '.'))

a = Analysis(
    ['plato_launcher.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce binary size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'pytest',
        'mypy',
        'black',
        'ruff',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='plato',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)