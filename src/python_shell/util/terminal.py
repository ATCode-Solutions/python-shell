"""
MIT License

Copyright (c) 2026 ATCode Solutions inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os

from python_shell.exceptions import ShellEnvironmentError
from python_shell.exceptions import UnsupportedShellError


__all__ = ('get_current_terminal_name', 'SUPPORTED_SHELLS')


SUPPORTED_SHELLS = frozenset(['bash', 'zsh', 'sh', 'dash', 'ksh', 'fish'])


def get_current_terminal_name():
    """Retrieve name of currently active terminal with validation
    
    Retrieves the shell name from the SHELL environment variable and
    validates it against known supported shells.
    
    Returns:
        str: The name of the current shell (e.g., 'bash', 'zsh')
    
    Raises:
        ShellEnvironmentError: If SHELL environment variable is not set
        UnsupportedShellError: If detected shell is not in SUPPORTED_SHELLS
    
    Note:
        This function relies on the SHELL environment variable which may not
        be available on all platforms (e.g., Windows). For best compatibility,
        ensure SHELL is properly set in your environment.
    """
    shell_path = os.environ.get('SHELL')
    
    if not shell_path:
        raise ShellEnvironmentError(
            "SHELL environment variable is not set. "
            "Please set SHELL to your shell executable path (e.g., /bin/bash)."
        )
    
    shell_name = os.path.basename(shell_path)
    
    if shell_name not in SUPPORTED_SHELLS:
        raise UnsupportedShellError(
            shell_name=shell_name,
            supported_shells=SUPPORTED_SHELLS
        )
    
    return shell_name
