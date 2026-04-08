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
from python_shell.exceptions import StreamDecodingError
from python_shell.exceptions import UnsupportedShellError
from python_shell.shell.terminal import TERMINAL_INTEGRATION_MAP
from python_shell.util import is_python2_running
from python_shell.util import get_current_terminal_name
from python_shell.util.streaming import decode_stream
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


class StreamDecodingTestCase(unittest.TestCase):
    """Test case for stream decoding"""

    def test_decode_stream_utf8_default(self):
        """Check that decode_stream works with UTF-8 by default"""
        stream = [b'Hello', b' ', b'World']
        result = decode_stream(stream)
        self.assertEqual(result, 'Hello World')

    def test_decode_stream_with_newlines(self):
        """Check that decode_stream handles newlines correctly"""
        stream = [b'Line 1\n', b'Line 2\n']
        result = decode_stream(stream)
        self.assertEqual(result, 'Line 1\nLine 2\n')

    def test_decode_stream_empty(self):
        """Check that decode_stream handles empty stream"""
        stream = []
        result = decode_stream(stream)
        self.assertEqual(result, '')

    def test_decode_stream_single_chunk(self):
        """Check that decode_stream handles single chunk"""
        stream = [b'Single chunk']
        result = decode_stream(stream)
        self.assertEqual(result, 'Single chunk')

    def test_decode_stream_latin1_encoding(self):
        """Check that decode_stream supports different encodings"""
        stream = [b'\xa9 2026']
        result = decode_stream(stream, encoding='latin-1')
        self.assertEqual(result, '\xa9 2026')

    def test_decode_stream_invalid_utf8_replace(self):
        """Check that decode_stream replaces invalid UTF-8 bytes by default"""
        stream = [b'Valid', b' text ', b'\xff\xfe', b' more']
        result = decode_stream(stream)
        
        self.assertIn('Valid', result)
        self.assertIn('text', result)
        self.assertIn('more', result)
        self.assertTrue('\ufffd' in result or '?' in result)

    def test_decode_stream_invalid_utf8_ignore(self):
        """Check that decode_stream can ignore invalid bytes"""
        stream = [b'Valid', b' text ', b'\xff\xfe', b' more']
        result = decode_stream(stream, errors='ignore')
        
        self.assertEqual(result, 'Valid text  more')

    def test_decode_stream_invalid_utf8_strict(self):
        """Check that decode_stream raises error in strict mode"""
        stream = [b'Valid', b' text ', b'\xff\xfe']
        
        with self.assertRaises(StreamDecodingError) as ctx:
            decode_stream(stream, errors='strict')
        
        error_str = str(ctx.exception)
        self.assertIn('Failed to decode', error_str)
        self.assertIn('utf-8', error_str)
        self.assertIn('Context:', error_str)

    def test_decode_stream_mixed_valid_invalid(self):
        """Check that decode_stream handles mixed valid/invalid content"""
        stream = [b'Start ', b'valid\n', b'\x80\x81', b' End']
        result = decode_stream(stream, errors='replace')
        
        self.assertIn('Start', result)
        self.assertIn('valid', result)
        self.assertIn('End', result)

    def test_decode_stream_empty_chunks(self):
        """Check that decode_stream handles empty chunks"""
        stream = [b'Hello', b'', b'World']
        result = decode_stream(stream)
        self.assertEqual(result, 'HelloWorld')

    def test_decode_stream_unicode_characters(self):
        """Check that decode_stream handles Unicode correctly"""
        stream = [b'Hello \xc2\xa9', b' \xe2\x9c\x93']
        result = decode_stream(stream)
        self.assertEqual(result, 'Hello \xa9 \u2713')

    def test_stream_decoding_error_has_context(self):
        """Check that StreamDecodingError includes security context"""
        exc = StreamDecodingError('utf-8')
        
        error_str = str(exc)
        self.assertIn('Failed to decode', error_str)
        self.assertIn('utf-8', error_str)
        self.assertIn('Context:', error_str)
        self.assertIn('timestamp=', error_str)

    def test_decode_stream_backward_compatible(self):
        """Check that decode_stream works with no parameters (backward compatible)"""
        stream = [b'Test ', b'backward ', b'compatibility']
        result = decode_stream(stream)
        self.assertEqual(result, 'Test backward compatibility')
