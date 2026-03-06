import os
import re

def detect_default_shell() -> str:
    """
    Attempts to detect the current active shell.
    Falls back to 'bash' on POSIX and 'pwsh'/'cmd' on Windows.
    """
    if os.name == 'nt':
        # Check if PowerShell module path is in environment
        if 'PSModulePath' in os.environ:
            return 'pwsh'
        return 'cmd'
    else:
        # Default to bash for Linux/macOS
        shell_env = os.environ.get('SHELL', '').lower()
        if 'zsh' in shell_env:
            return 'zsh'
        return 'bash'

def minify_to_oneliner(code: str, shell_type: str) -> str:
    """
    Strips comments and newlines, joining commands appropriately for the target shell.
    """
    lines = code.strip().splitlines()
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Skip empty lines and full-line comments
        if not stripped or stripped.startswith('#') or stripped.startswith('REM '):
            continue
        processed_lines.append(stripped)

    if not processed_lines:
        return ""

    # Join logic based on shell
    if shell_type in ['cmd']:
        return " && ".join(processed_lines)
    elif shell_type in ['bash', 'zsh', 'pwsh', 'powershell']:
        return "; ".join(processed_lines)
    else:
        # Fallback
        return "; ".join(processed_lines)

def inject_uv_header(code: str) -> str:
    """
    Checks if a Python script has a PEP 723 uv header.
    If not, injects a minimal default header so `uv run` works seamlessly.
    """
    if "# /// script" in code:
        return code

    default_header = """# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
    return default_header + "\n" + code.lstrip()