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

__all__ = ('BaseShellException',)


class BaseShellException(Exception):
    """Base exception for all exceptions within the library
    
    Includes security-relevant context for auditing and forensics:
    - timestamp: When the exception occurred
    - user: User who executed the command
    - cwd: Current working directory
    - pid: Process ID
    """
    
    def __init__(self, *args, **kwargs):
        super(BaseShellException, self).__init__(*args, **kwargs)
        
        # Capture context at exception creation time
        self.timestamp = datetime.datetime.utcnow()
        self.user = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
        try:
            self.cwd = os.getcwd()
        except OSError:
            self.cwd = 'unknown'
        self.pid = os.getpid()
    
    def get_context_string(self):
        """Returns formatted context information for logging/debugging
        
        Returns:
            str: Formatted context with timestamp, user, cwd, and pid
        """
        return (
            "Context: timestamp={timestamp}, user={user}, cwd={cwd}, pid={pid}"
        ).format(
            timestamp=self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
            user=self.user,
            cwd=self.cwd,
            pid=self.pid
        )
