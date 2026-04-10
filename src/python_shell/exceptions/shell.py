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

from .base import BaseShellException


__all__ = ('CommandDoesNotExist', 'ShellException', 'ShellEnvironmentError', 'UnsupportedShellError')


class ShellException(BaseShellException):
    """Defines any exception caused by commands run in Shell"""

    _command = None

    def __init__(self, command):
        super(ShellException, self).__init__()
        self._command = command

    def __str__(self):
        base_msg = 'Shell command "{} {}" failed with return code {}'.format(
            self._command.command,
            self._command.arguments,
            self._command.return_code)
        return '{} [{}]'.format(base_msg, self.get_context_string())


class CommandDoesNotExist(ShellException):
    """Defines an exception when command does not exist in the environment"""
    def __init__(self, command):
        super(CommandDoesNotExist, self).__init__(command)

    def __str__(self):
        base_msg = 'Command "{}" does not exist'.format(self._command.command)
        return '{} [{}]'.format(base_msg, self.get_context_string())


class ShellEnvironmentError(BaseShellException):
    """Raised when SHELL environment variable is not set or invalid"""
    
    def __init__(self, message):
        super(ShellEnvironmentError, self).__init__()
        self._message = message
    
    def __str__(self):
        return '{} [{}]'.format(self._message, self.get_context_string())


class UnsupportedShellError(BaseShellException):
    """Raised when detected shell is not supported"""
    
    def __init__(self, shell_name, supported_shells):
        super(UnsupportedShellError, self).__init__()
        self._shell_name = shell_name
        self._supported_shells = supported_shells
    
    def __str__(self):
        base_msg = 'Unsupported shell: "{}". Supported shells: {}'.format(
            self._shell_name,
            ', '.join(sorted(self._supported_shells))
        )
        return '{} [{}]'.format(base_msg, self.get_context_string())
