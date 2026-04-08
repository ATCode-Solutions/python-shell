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
import sys
import unittest

from python_shell.exceptions import ShellEnvironmentError
from python_shell.exceptions import UnsupportedShellError
from python_shell.shell.terminal import TERMINAL_INTEGRATION_MAP
from python_shell.util import is_python2_running
from python_shell.util import get_current_terminal_name
from python_shell.util.terminal import SUPPORTED_SHELLS


__all__ = ('UtilTestCase',)


class UtilTestCase(unittest.TestCase):
    """Test case for utils"""

    def test_python_version_checker(self):
        """Check if python version checker works properly"""
        self.assertEqual(is_python2_running(), sys.version_info[0] == 2)

    def test_get_current_terminal_name(self):
        """Check that getting current terminal name works"""
        self.assertIn(get_current_terminal_name(),
                      TERMINAL_INTEGRATION_MAP.keys())

    def test_get_current_terminal_name_validates(self):
        """Check that terminal name is validated"""
        terminal_name = get_current_terminal_name()
        self.assertIn(terminal_name, SUPPORTED_SHELLS)

    def test_get_current_terminal_missing_shell_var(self):
        """Check that missing SHELL variable raises ShellEnvironmentError"""
        original_shell = os.environ.get('SHELL')
        
        try:
            if 'SHELL' in os.environ:
                del os.environ['SHELL']
            
            with self.assertRaises(ShellEnvironmentError) as ctx:
                get_current_terminal_name()
            
            self.assertIn('SHELL environment variable is not set', str(ctx.exception))
        finally:
            if original_shell:
                os.environ['SHELL'] = original_shell

    def test_get_current_terminal_unsupported_shell(self):
        """Check that unsupported shell raises UnsupportedShellError"""
        original_shell = os.environ.get('SHELL')
        
        try:
            os.environ['SHELL'] = '/bin/unsupported_shell_xyz'
            
            with self.assertRaises(UnsupportedShellError) as ctx:
                get_current_terminal_name()
            
            error_msg = str(ctx.exception)
            self.assertIn('unsupported_shell_xyz', error_msg)
            self.assertIn('Supported shells:', error_msg)
        finally:
            if original_shell:
                os.environ['SHELL'] = original_shell
            else:
                if 'SHELL' in os.environ:
                    del os.environ['SHELL']

    def test_supported_shells_constant(self):
        """Check that SUPPORTED_SHELLS contains expected shells"""
        expected_shells = {'bash', 'zsh', 'sh', 'dash', 'ksh', 'fish'}
        self.assertEqual(SUPPORTED_SHELLS, expected_shells)
