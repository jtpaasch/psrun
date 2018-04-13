"""Unit tests for the ``lib.proc`` module."""

from unittest import TestCase
from unittest.mock import call, patch, Mock

from queue import Queue
import io

from psrun.lib import exceptions
from psrun.lib import proc


class TestProc(TestCase):
    """Test suite for the ``lib.proc`` module."""

    def test_try_monitor(self):
        """Ensure ``try_monitor()`` monitors a process."""
        log = "dummy-log"
        pid = "dummy-pid"

        p = patch("{}.monitor.collect".format(proc.__name__))
        with p as collect:
            proc.try_monitor(log, pid)
            collect.assert_called_once_with(log, pid)

    def test_try_monitor_with_errors(self):
        """Ensure ``try_monitor()`` logs errors."""
        data = []
        log = data.append
        pid = "dummy-pid"

        p = patch("{}.monitor.collect".format(proc.__name__))
        with p as collect:
            collect.side_effect = Exception("dummy-error")

            proc.try_monitor(log, pid)
            self.assertTrue("dummy-error" in data[0])

    def test_read_buffer(self):
        """Ensure ``read_buffer()`` pops all lines from a buffer."""
        output = []
        log = output.append
        buf = Queue()

        lines = [b"line 1\n", b"line 2\n", b"line 3\n"]
        expected = []

        for line in lines:
            buf.put(line)
            expected.append(line.decode("utf8").rstrip())

        proc.read_buffer(buf, log)
        self.assertEqual(output, expected)

    def test_start(self):
        """Ensure ``start()`` starts a process."""
        proc_object = Mock()
        p = patch("{}.subprocess.Popen".format(proc.__name__))
        with p as popen:
            popen.return_value = proc_object

            result = proc.start(["dummy", "command"])
            self.assertEqual(result, proc_object)

    def test_start_when_permission_denied(self):
        """Ensure ``start()`` raises when permission is denied."""
        p = patch("{}.subprocess.Popen".format(proc.__name__))
        with p as popen:
            popen.side_effect = PermissionError

            with self.assertRaises(exceptions.PermissionDenied):
                proc.start(["dummy", "command"])

    def test_stop(self):
        """Ensure ``stop()`` terminates a process."""
        shutdown = None
        term_code = 15

        p = Mock()
        p.poll = Mock()
        p.terminate = Mock()
        p.kill = Mock()

        p.poll.return_value = term_code

        proc.stop(p, shutdown)

        self.assertTrue(p.terminate.called)
        self.assertFalse(p.kill.called)

    def test_stop_and_kill(self):
        """Ensure ``stop()`` kills a process after a time."""
        shutdown = 0.1

        p = Mock()
        p.poll = Mock()
        p.terminate = Mock()
        p.kill = Mock()

        p.poll.return_value = None

        proc.stop(p, shutdown)

        self.assertTrue(p.terminate.called)
        self.assertTrue(p.kill.called)

    def test_execute(self):
        """Ensure ``execute()`` runs a process."""
        stdout_lines = [b"stdout 1\n", b"stdout 2\n", b"stdout 3\n"]
        stdout_stream = b"".join(stdout_lines)
        stdout = io.BytesIO(stdout_stream)
        stdout_data = []
        stdout_log = stdout_data.append
        stdout_expected = [x.decode("utf8").rstrip() for x in stdout_lines]

        stderr_lines = [b"stderr 1\n", b"stderr 2\n", b"stderr 3\n"]
        stderr_stream = b"".join(stderr_lines)
        stderr = io.BytesIO(stderr_stream)
        stderr_data = []
        stderr_log = stderr_data.append
        stderr_expected = [x.decode("utf8").rstrip() for x in stderr_lines]

        ps_log = Mock()

        timeout = None
        shutdown = None

        pid = 10
        p = Mock(pid=pid)

        p.stdout = stdout
        p.stderr = stderr

        p.poll = Mock()
        p.poll.side_effect = [None, 0, 0]

        p1 = patch("{}.start".format(proc.__name__))
        p2 = patch("{}.try_monitor".format(proc.__name__))
        with p1 as start, p2 as try_monitor:
            start.return_value = p

            args = [
                ["some-cmd"], stdout_log, stderr_log, ps_log,
                timeout, shutdown]
            exit_code, running_time = proc.execute(*args)

            calls = [call(ps_log, pid), call(ps_log, pid)]
            try_monitor.assert_has_calls(calls)

            self.assertEqual(exit_code, 0)
            self.assertEqual(stdout_data, stdout_expected)
            self.assertEqual(stderr_data, stderr_expected)

    def test_execute_with_timeout(self):
        """Ensure ``execute()`` handles timeouts."""
        stdout = io.BytesIO(b"")
        stdout_data = []
        stdout_log = stdout_data.append

        stderr = io.BytesIO(b"")
        stderr_data = []
        stderr_log = stderr_data.append

        ps_log = Mock()

        timeout = 0.1
        shutdown = 0.1

        pid = 10
        p = Mock(pid=pid)

        p.stdout = stdout
        p.stderr = stderr

        p.poll = Mock()
        p.poll.side_effect = [None, None, 15, 15]

        p1 = patch("{}.start".format(proc.__name__))
        p2 = patch("{}.try_monitor".format(proc.__name__))
        with p1 as start, p2:
            start.return_value = p

            args = [
                ["some-cmd"], stdout_log, stderr_log, ps_log,
                timeout, shutdown]
            with self.assertRaises(exceptions.ProcTimeout):
                proc.execute(*args)
