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

import logging

from python_shell.exceptions import StreamDecodingError


__all__ = ('decode_stream',)

_security_logger = logging.getLogger('python_shell.security.stream')


def decode_stream(stream, encoding='utf-8', errors='replace'):
    try:
        decoded_chunks = []
        for chunk in stream:
            try:
                if isinstance(chunk, bytes):
                    decoded_chunks.append(chunk.decode(encoding, errors=errors))
                else:
                    decoded_chunks.append(chunk)
            except (UnicodeDecodeError, AttributeError) as e:
                _security_logger.warning(
                    "Stream decoding warning: encoding=%s, errors=%s, error=%s",
                    encoding, errors, str(e)
                )
                
                if errors == 'strict':
                    raise StreamDecodingError(encoding, e)
                
                continue
        
        return ''.join(decoded_chunks)
    
    except StreamDecodingError:
        raise
    except Exception as e:
        _security_logger.error(
            "Unexpected error during stream decoding: encoding=%s, error=%s, type=%s",
            encoding, str(e), type(e).__name__
        )
        raise StreamDecodingError(encoding, e)
