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

import time
import threading
import unittest

from python_shell.exceptions import ProcessTimeoutError
from python_shell.exceptions import UndefinedProcess
from python_shell.shell.processing.process import AsyncProcess
from python_shell.shell.processing.process import Process
from python_shell.shell.processing.process import StreamIterator
from python_shell.shell.processing.process import SyncProcess
from python_shell.shell.processing.process import Subprocess
from python_shell.util.streaming import decode_stream


class FakeBaseProcess(Process):
    """Fake Process implementation"""

    def execute(self):
        """Wrapper for running execute() of parent"""

        return super(FakeBaseProcess, self).execute()


class SyncProcessTestCase(unittest.TestCase):
    """Test case for synchronous process wrapper"""

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
            p._process.stderr and p._process.stderr.close()
            p._process.stdout and p._process.stdout.close()

    def _test_sync_process_is_finished(self):
        sync_process_args = ['echo', 'Hello']
        sync_process_kwargs = {
            'stdout': Subprocess.DEVNULL,
            'stderr': Subprocess.DEVNULL
        }
        process = SyncProcess(*sync_process_args,
                              **sync_process_kwargs)
        self.processes.append(process)

        self.assertIsNone(process.returncode)
        self.assertIsNone(process.is_finished)
        self.assertIsNone(process.is_terminated)

        process.execute()
        self.assertIsNotNone(process.returncode)
        self.assertTrue(process.is_finished)

    def _test_sync_process_not_initialized(self):
        """Check process which was not initialized"""
        process = SyncProcess(['ls'])
        self.processes.append(process)
        self.assertTrue(process.is_undefined)

    def test_sync_process_property_is_finished(self):
        """Check that is_finished works well for SyncProcess"""
        self._test_sync_process_is_finished()
        # TODO(albartash): Check for not finished process is TBD:
        #                  It needs a proper implementation,
        #                  as SyncProcess blocks main thread.
        self._test_sync_process_not_initialized()

    def test_sync_process_termination(self):
        """Check that SyncProcess can be terminated properly"""
        self.skipTest("TODO")

    def test_sync_process_completion(self):
        """Check that SyncProcess can be completed properly"""
        self.skipTest("TODO")


class AsyncProcessTestCase(unittest.TestCase):
    """Test case for asynchronous process wrapper"""

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
            p._process.stderr and p._process.stderr.close()
            p._process.stdout and p._process.stdout.close()

    def test_async_process_is_finished(self):
        timeout = 0.1  # seconds
        process = AsyncProcess('sleep', str(timeout))
        self.processes.append(process)

        self.assertIsNone(process.returncode)
        self.assertIsNone(process.is_finished)
        self.assertIsNone(process.is_terminated)

        process.execute()
        self.assertIsNone(process.returncode)
        time.sleep(timeout + 1)  # ensure command finishes
        self.assertEqual(process.returncode, 0)

    def test_async_process_is_not_initialized(self):
        """Check that async process is not initialized when not finished"""
        timeout = 0.5  # seconds
        process = AsyncProcess('sleep', str(timeout))
        self.processes.append(process)
        self.assertTrue(process.is_undefined)
        process.execute()
        self.assertIsNone(process.returncode)
        time.sleep(timeout + 0.5)
        self.assertIsNotNone(process.returncode)

    def test_async_std_properties_accessible(self):
        """Check if standard properties are accessible for AsyncProcess"""

        timeout = 0.5  # seconds
        process = AsyncProcess('sleep', str(timeout))
        self.processes.append(process)
        process.execute()
        stdout = decode_stream(process.stdout)
        stderr = decode_stream(process.stderr)

        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    def test_async_process_property_is_finished(self):
        self.skipTest("TODO")

    def test_async_process_termination(self):
        """Check that AsyncProcess can be terminated properly"""

        process = AsyncProcess('yes')
        self.processes.append(process)
        process.execute()
        process.terminate()

        self.assertTrue(process.is_terminated)
        self.assertEqual(process.returncode, -15)

    def test_async_process_completion(self):
        """Check that AsyncProcess can be completed properly"""

        timeout = str(0.5)
        process = AsyncProcess('sleep', timeout)
        self.processes.append(process)
        process.execute()
        process.wait()
        self.assertTrue(process.is_finished)
        self.assertEqual(process.returncode, 0)

    def test_async_process_timeout_enforced(self):
        """Check that timeout is enforced for long-running processes"""

        process = AsyncProcess('sleep', '10', timeout=1)
        self.processes.append(process)
        process.execute()
        
        time.sleep(1.5)
        
        with self.assertRaises(ProcessTimeoutError):
            process.check_timeout()
        
        self.assertTrue(process.is_finished)

    def test_async_process_timeout_not_exceeded(self):
        """Check that check_timeout returns True when within timeout"""

        process = AsyncProcess('sleep', '2', timeout=5)
        self.processes.append(process)
        process.execute()
        
        time.sleep(0.5)
        
        result = process.check_timeout()
        self.assertTrue(result)

    def test_async_process_elapsed_time(self):
        """Check that elapsed_time property works correctly"""

        process = AsyncProcess('sleep', '1', timeout=5)
        self.processes.append(process)
        
        self.assertIsNone(process.elapsed_time)
        
        process.execute()
        time.sleep(0.5)
        
        elapsed = process.elapsed_time
        self.assertIsNotNone(elapsed)
        self.assertGreaterEqual(elapsed, 0.5)
        self.assertLess(elapsed, 1.0)

    def test_async_process_timeout_property(self):
        """Check that timeout property returns configured timeout"""

        process = AsyncProcess('echo', 'test', timeout=42)
        self.processes.append(process)
        process.execute()
        
        self.assertEqual(process.timeout, 42)

    def test_async_process_default_timeout(self):
        """Check that default timeout is set when not specified"""

        process = AsyncProcess('echo', 'test')
        self.processes.append(process)
        process.execute()
        
        self.assertEqual(process.timeout, AsyncProcess.DEFAULT_TIMEOUT)

    def test_async_process_check_timeout_undefined_process(self):
        """Check that check_timeout raises for undefined process"""

        process = AsyncProcess('echo', 'test')
        self.processes.append(process)
        
        with self.assertRaises(UndefinedProcess):
            process.check_timeout()


class ProcessTestCase(unittest.TestCase):
    """Test case for Process class"""

    def test_execution_of_base_process(self):
        """Check execution of Process instance"""

        with self.assertRaises(NotImplementedError):
            FakeBaseProcess(None).execute()


class StreamIteratorTestCase(unittest.TestCase):
    """Test case for StreamIterator instance"""

    def test_stream_is_not_set(self):
        """Check work of iterator when stream is not passed"""

        stream = StreamIterator(stream=None)
        with self.assertRaises(StopIteration):
            next(stream)


class SubprocessTestCase(unittest.TestCase):
    """Test case for Subprocess wrapper"""

    def test_devnull_property_accessible(self):
        """Check that DEVNULL property is accessible"""
        devnull = Subprocess.DEVNULL
        self.assertIsNotNone(devnull)

    def test_devnull_property_consistent(self):
        """Check that DEVNULL property returns same value on multiple calls"""
        devnull1 = Subprocess.DEVNULL
        devnull2 = Subprocess.DEVNULL
        self.assertEqual(devnull1, devnull2)

    def test_devnull_cleanup_registered(self):
        """Check that cleanup handler is registered for Python 2"""
        import sys
        devnull = Subprocess.DEVNULL
        
        if sys.version_info[0] == 2:
            from python_shell.shell.processing.process import _SubprocessMeta
            self.assertTrue(_SubprocessMeta._devnull_cleanup_registered)


class ThreadSafetyTestCase(unittest.TestCase):
    """Test case for thread safety of Process classes"""

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
            p._process.stderr and p._process.stderr.close()
            p._process.stdout and p._process.stdout.close()

    def test_concurrent_returncode_access(self):
        """Check that returncode can be accessed safely from multiple threads"""
        process = AsyncProcess('sleep', '1')
        self.processes.append(process)
        process.execute()
        
        results = []
        errors = []
        
        def access_returncode():
            try:
                for _ in range(10):
                    rc = process.returncode
                    results.append(rc)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=access_returncode) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent access")
        self.assertGreater(len(results), 0, "Should have collected returncode values")

    def test_concurrent_is_finished_access(self):
        """Check that is_finished can be accessed safely from multiple threads"""
        process = AsyncProcess('sleep', '0.5')
        self.processes.append(process)
        process.execute()
        
        results = []
        errors = []
        
        def access_is_finished():
            try:
                for _ in range(10):
                    finished = process.is_finished
                    results.append(finished)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=access_is_finished) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent access")
        self.assertGreater(len(results), 0, "Should have collected is_finished values")

    def test_concurrent_is_terminated_access(self):
        """Check that is_terminated can be accessed safely from multiple threads"""
        process = AsyncProcess('sleep', '10')
        self.processes.append(process)
        process.execute()
        
        results = []
        errors = []
        
        def access_is_terminated():
            try:
                for _ in range(5):
                    terminated = process.is_terminated
                    results.append(terminated)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=access_is_terminated) for _ in range(3)]
        for t in threads:
            t.start()
        
        time.sleep(0.2)
        process.terminate()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent access")
        self.assertGreater(len(results), 0, "Should have collected is_terminated values")

    def test_concurrent_terminate_calls(self):
        """Check that multiple concurrent terminate calls are safe"""
        process = AsyncProcess('sleep', '10')
        self.processes.append(process)
        process.execute()
        
        errors = []
        
        def terminate_process():
            try:
                process.terminate()
            except UndefinedProcess:
                pass
            except Exception as e:
                errors.append(e)
        
        time.sleep(0.1)
        
        threads = [threading.Thread(target=terminate_process) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent termination")
        self.assertTrue(process.is_terminated)

    def test_concurrent_wait_calls(self):
        """Check that multiple concurrent wait calls are safe"""
        process = AsyncProcess('sleep', '0.5')
        self.processes.append(process)
        process.execute()
        
        errors = []
        
        def wait_for_process():
            try:
                process.wait()
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=wait_for_process) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent wait")
        self.assertTrue(process.is_finished)

    def test_concurrent_check_timeout_calls(self):
        """Check that check_timeout can be called safely from multiple threads"""
        process = AsyncProcess('sleep', '1', timeout=5)
        self.processes.append(process)
        process.execute()
        
        errors = []
        results = []
        
        def check_timeout():
            try:
                result = process.check_timeout()
                results.append(result)
            except ProcessTimeoutError:
                pass
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=check_timeout) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent timeout checks")

    def test_process_has_lock_attribute(self):
        """Check that Process instances have a lock attribute"""
        process = AsyncProcess('echo', 'test')
        self.processes.append(process)
        
        self.assertTrue(hasattr(process, '_lock'), "Process should have _lock attribute")
        self.assertIsInstance(process._lock, threading.Lock, "Lock should be threading.Lock instance")
