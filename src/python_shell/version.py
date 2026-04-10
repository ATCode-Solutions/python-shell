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

try:
    import pkg_resources
    _has_pkg_resources = True
except ImportError:
    _has_pkg_resources = False


__all__ = ('get_version',)


def get_version():
    """Retrieves version of the current root package"""
    
    if _has_pkg_resources:
        try:
            return pkg_resources.require('python_shell')[0].version.strip()
        except Exception:
            pass
    
    version_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '..',
        'VERSION'
    )
    
    try:
        with open(version_file, 'r') as f:
            return f.read().strip()
    except (IOError, OSError):
        return 'unknown'
