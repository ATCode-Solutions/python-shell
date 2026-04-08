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

import datetime
import os
import sys
import time
import unittest

from python_shell.command import Command
from python_shell.shell.processing.process import AsyncProcess
from python_shell.shell.processing.process import SyncProcess
from python_shell import exceptions


__all__ = ('ExceptionTestCase',)


class ExceptionTestCase(unittest.TestCase):
    """Tests for exceptions classes"""

    def test_command_does_not_exist(self):
        """Check that CommandDoesNotExist works properly"""

        cmd_name = "test_{}".format(time.time())
        with self.assertRaises(exceptions.CommandDoesNotExist) as context:
            cmd = Command(cmd_name)
            raise exceptions.CommandDoesNotExist(cmd)
        
        error_str = str(context.exception)
        self.assertIn('Command "{}" does not exist'.format(cmd_name), error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('timestamp=', error_str)
        self.assertIn('user=', error_str)
        self.assertIn('cwd=', error_str)
        self.assertIn('pid=', error_str)

    def test_undefined_process(self):
        """Check exception for Undefined process"""

        for method in ('wait', 'terminate'):
            for process_cls in (SyncProcess, AsyncProcess):
                try:
                    process = process_cls('ls')
                    getattr(process, method)()
                except exceptions.UndefinedProcess as e:
                    error_str = str(e)
                    self.assertIn("Undefined process cannot be used", error_str)
                    self.assertIn('Context:', error_str)
                else:
                    self.fail("UndefinedProcess was not thrown")

    def test_run_process_error(self):
        """Check exception for running process (now raises CommandNotFoundError)"""

        for process_cls in (SyncProcess, AsyncProcess):
            try:
                process = process_cls('sleepa', 'asd')
                process.execute()
            except exceptions.CommandNotFoundError as e:
                error_str = str(e)
                self.assertIn('sleepa', error_str)
                self.assertIn('not found', error_str.lower())
                self.assertIn('Context:', error_str)
            else:
                self.fail("CommandNotFoundError was not thrown")


class ExceptionContextTestCase(unittest.TestCase):
    """Tests for exception context attributes"""

    def test_base_exception_has_context_attributes(self):
        """Check that BaseShellException captures context"""
        exc = exceptions.BaseShellException("test error")
        
        self.assertIsInstance(exc.timestamp, datetime.datetime)
        self.assertIsNotNone(exc.user)
        self.assertIsNotNone(exc.cwd)
        self.assertIsInstance(exc.pid, int)
        self.assertEqual(exc.pid, os.getpid())

    def test_base_exception_context_string(self):
        """Check that get_context_string returns formatted context"""
        exc = exceptions.BaseShellException("test error")
        context_str = exc.get_context_string()
        
        self.assertIn('Context:', context_str)
        self.assertIn('timestamp=', context_str)
        self.assertIn('user=', context_str)
        self.assertIn('cwd=', context_str)
        self.assertIn('pid=', context_str)
        self.assertIn(str(os.getpid()), context_str)

    def test_command_does_not_exist_exception_includes_context(self):
        """Check that CommandDoesNotExist includes context in string representation"""
        cmd = Command('nonexistent_command_12345')
        exc = exceptions.CommandDoesNotExist(cmd)
        
        error_str = str(exc)
        self.assertIn('Command', error_str)
        self.assertIn('does not exist', error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('timestamp=', error_str)
        self.assertIn('user=', error_str)

    def test_shell_environment_error_includes_context(self):
        """Check that ShellEnvironmentError includes context"""
        exc = exceptions.ShellEnvironmentError("SHELL not set")
        
        error_str = str(exc)
        self.assertIn('SHELL not set', error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('user=', error_str)
        self.assertIn('cwd=', error_str)

    def test_unsupported_shell_error_includes_context(self):
        """Check that UnsupportedShellError includes context"""
        exc = exceptions.UnsupportedShellError('tcsh', frozenset(['bash', 'zsh']))
        
        error_str = str(exc)
        self.assertIn('Unsupported shell: "tcsh"', error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('pid=', error_str)

    def test_process_timeout_error_includes_context(self):
        """Check that ProcessTimeoutError includes context"""
        exc = exceptions.ProcessTimeoutError(timeout=30, command='sleep')
        
        error_str = str(exc)
        self.assertIn("Process 'sleep' exceeded timeout of 30 seconds", error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('timestamp=', error_str)

    def test_run_process_error_includes_context(self):
        """Check that RunProcessError includes context"""
        exc = exceptions.RunProcessError('test_cmd', process_args=['arg1', 'arg2'])
        
        error_str = str(exc)
        self.assertIn("Fail to run 'test_cmd", error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('user=', error_str)

    def test_undefined_process_includes_context(self):
        """Check that UndefinedProcess includes context"""
        exc = exceptions.UndefinedProcess()
        
        error_str = str(exc)
        self.assertIn('Undefined process cannot be used', error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('cwd=', error_str)

    def test_exception_context_timestamp_is_recent(self):
        """Check that exception timestamp is captured at creation time"""
        before = datetime.datetime.utcnow()
        exc = exceptions.BaseShellException("test")
        after = datetime.datetime.utcnow()
        
        self.assertGreaterEqual(exc.timestamp, before)
        self.assertLessEqual(exc.timestamp, after)

    def test_exception_context_user_from_environment(self):
        """Check that user is captured from environment"""
        exc = exceptions.BaseShellException("test")
        
        # User should be captured from USER or USERNAME env var
        expected_user = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
        self.assertEqual(exc.user, expected_user)


class SpecificExceptionHandlingTestCase(unittest.TestCase):
    """Test case for specific exception handling"""

    processes = []

    def tearDown(self):
        """Cleanup processes"""
        for p in self.processes:
            if not p._process:
                continue
            try:
                p._process.terminate()
                p._process.wait()
            except OSError:
                pass
            if p._process.stderr:
                p._process.stderr.close()
            if p._process.stdout:
                p._process.stdout.close()

    def test_command_not_found_error_sync(self):
        """Check that CommandNotFoundError is raised for non-existent command (SyncProcess)"""
        process = SyncProcess('nonexistent_command_xyz_12345')
        self.processes.append(process)
        
        with self.assertRaises(exceptions.CommandNotFoundError) as ctx:
            process.execute()
        
        error_str = str(ctx.exception)
        self.assertIn('nonexistent_command_xyz_12345', error_str)
        self.assertIn('not found', error_str.lower())
        self.assertIn('Context:', error_str)

    def test_command_not_found_error_async(self):
        """Check that CommandNotFoundError is raised for non-existent command (AsyncProcess)"""
        process = AsyncProcess('nonexistent_command_xyz_12345')
        self.processes.append(process)
        
        with self.assertRaises(exceptions.CommandNotFoundError) as ctx:
            process.execute()
        
        error_str = str(ctx.exception)
        self.assertIn('nonexistent_command_xyz_12345', error_str)
        self.assertIn('not found', error_str.lower())

    def test_invalid_argument_error_sync(self):
        """Check that InvalidArgumentError is raised for invalid arguments (SyncProcess)"""
        # Pass invalid stdin (not a file-like object or PIPE)
        process = SyncProcess('echo', 'test', stdin='invalid')
        self.processes.append(process)
        
        with self.assertRaises(exceptions.InvalidArgumentError) as ctx:
            process.execute()
        
        error_str = str(ctx.exception)
        self.assertIn('Invalid arguments', error_str)
        self.assertIn('echo', error_str)

    def test_invalid_argument_error_async(self):
        """Check that InvalidArgumentError is raised for invalid arguments (AsyncProcess)"""
        # Pass invalid stdin (not a file-like object or PIPE)
        process = AsyncProcess('echo', 'test', stdin='invalid')
        self.processes.append(process)
        
        with self.assertRaises(exceptions.InvalidArgumentError) as ctx:
            process.execute()
        
        error_str = str(ctx.exception)
        self.assertIn('Invalid arguments', error_str)

    def test_command_not_found_error_has_context(self):
        """Check that CommandNotFoundError includes security context"""
        exc = exceptions.CommandNotFoundError('missing_cmd')
        
        error_str = str(exc)
        self.assertIn('missing_cmd', error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('timestamp=', error_str)
        self.assertIn('user=', error_str)
        self.assertIn('pid=', error_str)

    def test_permission_denied_error_has_context(self):
        """Check that PermissionDeniedError includes security context"""
        exc = exceptions.PermissionDeniedError('/restricted/command')
        
        error_str = str(exc)
        self.assertIn('/restricted/command', error_str)
        self.assertIn('Permission denied', error_str)
        self.assertIn('Context:', error_str)

    def test_invalid_argument_error_has_context(self):
        """Check that InvalidArgumentError includes security context"""
        exc = exceptions.InvalidArgumentError('cmd', ['arg1', 'arg2'])
        
        error_str = str(exc)
        self.assertIn('cmd', error_str)
        self.assertIn('Invalid arguments', error_str)
        self.assertIn('Context:', error_str)

    def test_exceptions_exported_in_module(self):
        """Check that new exception types are exported"""
        self.assertTrue(hasattr(exceptions, 'CommandNotFoundError'))
        self.assertTrue(hasattr(exceptions, 'PermissionDeniedError'))
        self.assertTrue(hasattr(exceptions, 'InvalidArgumentError'))
