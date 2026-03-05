"""
MIT License

Copyright (c) 2020 Alex Sokolov

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

from python_shell.shell.terminal.base import BaseTerminalIntegration
from python_shell.util import SyncProcess
from python_shell.util import Subprocess
from python_shell.util.streaming import decode_stream


__all__ = ('BashTerminalIntegration', 'ZshTerminalIntegration', 'PosixShellIntegration')


class BashTerminalIntegration(BaseTerminalIntegration):
    """Terminal integration for Bash"""

    _shell_name = "bash"
    _available_commands = None

    def __init__(self):
        super(BashTerminalIntegration, self).__init__()

    def _get_available_commands(self):
        """Reload available commands from shell"""
        process = SyncProcess(
            self._shell_name, '-c', 'compgen -c',
            stdout=Subprocess.PIPE,
            stderr=Subprocess.DEVNULL,
            check=True
        )
        process.execute()
        return decode_stream(process.stdout).split()

    @property
    def available_commands(self):
        """Returns list of available executable commands in the shell"""
        if self._available_commands is None:
            self._available_commands = self._get_available_commands()
        return self._available_commands


class ZshTerminalIntegration(BaseTerminalIntegration):
    """Terminal integration for Zsh"""
    
    _shell_name = "zsh"
    _available_commands = None
    
    def __init__(self):
        super(ZshTerminalIntegration, self).__init__()
    
    def _get_available_commands(self):
        """Get available commands from zsh using compgen via bash emulation"""
        process = SyncProcess(
            self._shell_name, '-c', 'print -rl -- ${(ko)commands}',
            stdout=Subprocess.PIPE,
            stderr=Subprocess.DEVNULL,
            check=False
        )
        process.execute()
        
        if process.returncode != 0:
            posix_integration = PosixShellIntegration(self._shell_name)
            return posix_integration._get_available_commands()
        
        return decode_stream(process.stdout).split()
    
    @property
    def available_commands(self):
        """Returns list of available executable commands in the shell"""
        if self._available_commands is None:
            self._available_commands = self._get_available_commands()
        return self._available_commands


class PosixShellIntegration(BaseTerminalIntegration):
    """Terminal integration for POSIX-compatible shells (sh, dash, ksh, fish)
    
    These shells may not support 'compgen', so we use a fallback method
    that gets commands from PATH.
    """
    
    _shell_name = "sh"
    _available_commands = None
    
    def __init__(self, shell_name="sh"):
        super(PosixShellIntegration, self).__init__()
        self._shell_name = shell_name
    
    def _get_available_commands(self):
        """Get available commands by scanning PATH directories"""
        import os
        commands = []
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        for directory in path_dirs:
            if not os.path.isdir(directory):
                continue
            try:
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath) and os.access(filepath, os.X_OK):
                        if filename not in commands:
                            commands.append(filename)
            except (OSError, IOError):
                continue
        
        return sorted(commands)
    
    @property
    def available_commands(self):
        """Returns list of available executable commands in the shell"""
        if self._available_commands is None:
            self._available_commands = self._get_available_commands()
        return self._available_commands
