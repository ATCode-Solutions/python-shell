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


__all__ = (
    'RunProcessError',
    'UndefinedProcess',
    'ProcessTimeoutError',
    'CommandNotFoundError',
    'PermissionDeniedError',
    'InvalidArgumentError'
)


class ProcessException(BaseShellException):
    """General exception class for Process failures"""


class UndefinedProcess(ProcessException):
    """Raises when there's a try to use undefined process"""

    def __str__(self):
        base_msg = "Undefined process cannot be used"
        return '{} [{}]'.format(base_msg, self.get_context_string())


class RunProcessError(BaseShellException):
    """Raised when process fails to be run"""

    def __init__(self,
                 cmd,
                 process_args=None,
                 process_kwargs=None):
        super(RunProcessError, self).__init__()
        self._cmd = cmd
        self._args = process_args
        self._kwargs = process_kwargs

    def __str__(self):
        base_msg = "Fail to run '{cmd} {args}'".format(
            cmd=self._cmd,
            args=' '.join(self._args) if self._args else '',
        )
        return '{} [{}]'.format(base_msg, self.get_context_string())


class ProcessTimeoutError(ProcessException):
    """Raised when process exceeds timeout limit"""

    def __init__(self, timeout, command=None):
        super(ProcessTimeoutError, self).__init__()
        self._timeout = timeout
        self._command = command

    def __str__(self):
        if self._command:
            base_msg = "Process '{cmd}' exceeded timeout of {timeout} seconds".format(
                cmd=self._command,
                timeout=self._timeout
            )
        else:
            base_msg = "Process exceeded timeout of {timeout} seconds".format(
                timeout=self._timeout
            )
        return '{} [{}]'.format(base_msg, self.get_context_string())


class CommandNotFoundError(ProcessException):
    """Raised when command executable is not found"""

    def __init__(self, command, original_error=None):
        super(CommandNotFoundError, self).__init__()
        self._command = command
        self._original_error = original_error

    def __str__(self):
        base_msg = "Command '{}' not found".format(self._command)
        if self._original_error:
            base_msg = "{}: {}".format(base_msg, str(self._original_error))
        return '{} [{}]'.format(base_msg, self.get_context_string())


class PermissionDeniedError(ProcessException):
    """Raised when insufficient permissions to execute command"""

    def __init__(self, command, original_error=None):
        super(PermissionDeniedError, self).__init__()
        self._command = command
        self._original_error = original_error

    def __str__(self):
        base_msg = "Permission denied to execute '{}'".format(self._command)
        if self._original_error:
            base_msg = "{}: {}".format(base_msg, str(self._original_error))
        return '{} [{}]'.format(base_msg, self.get_context_string())


class InvalidArgumentError(ProcessException):
    """Raised when invalid arguments provided to process"""

    def __init__(self, command, args, original_error=None):
        super(InvalidArgumentError, self).__init__()
        self._command = command
        self._args = args
        self._original_error = original_error

    def __str__(self):
        base_msg = "Invalid arguments for command '{}': {}".format(
            self._command,
            ' '.join(str(a) for a in self._args) if self._args else 'N/A'
        )
        if self._original_error:
            base_msg = "{}: {}".format(base_msg, str(self._original_error))
        return '{} [{}]'.format(base_msg, self.get_context_string())
