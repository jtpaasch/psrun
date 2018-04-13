"""Unit tests for the ``lib.main`` module."""

from unittest import TestCase
from unittest.mock import patch, Mock

from psrun.lib import exceptions
from psrun.lib import main


class TestMain(TestCase):
    """Test suite for the ``libe.main`` module."""

    def test_report_start_details(self):
        """Ensure ``report_start_details()`` logs something."""
        log = Mock()
        result = main.report_start_details(log, "cmd -al")
        self.assertTrue(log.called)
        self.assertIsNone(result)

    def test_report_final_details(self):
        """Ensure ``report_final_details()`` logs something."""
        log = Mock()
        result = main.report_final_details(log, "exit-code", "run-time")
        self.assertTrue(log.called)
        self.assertIsNone(result)

    def test_report_error(self):
        """Ensure ``report_error()`` logs something."""
        log = Mock()
        result = main.report_error(log, "some-error")
        self.assertTrue(log.called)
        self.assertIsNone(result)

    def test_run(self):
        """Ensure ``run`` executes a command and reports correctly."""
        runner_log = Mock()
        ps_log = Mock()
        stdout_log = Mock()
        stderr_log = Mock()
        cmd = "cmd -al"
        timeout = "dummy-timeout"
        shutdown = "dummy-shutdown"
        exit_code = "dummy-exit-code"
        running_time = "dummy-running-time"

        p = patch("{}.proc.execute".format(main.__name__))
        with p as proc_execute:
            proc_execute.return_value = (exit_code, running_time)

            main.run(
                cmd, timeout, shutdown, runner_log, ps_log,
                stdout_log, stderr_log)

            proc_execute.assert_called_once_with(
                cmd, stdout_log, stderr_log, ps_log, timeout, shutdown)

    def test_run_handles_errors(self):
        """Ensure ``run()`` reports errors."""
        runner_log = Mock()
        ps_log = Mock()
        stdout_log = Mock()
        stderr_log = Mock()
        cmd = "cmd -al"
        timeout = "dummy-timeout"
        shutdown = "dummy-shutdown"
        errors = [exceptions.ProcTimeout, exceptions.PermissionDenied]

        p1 = patch("{}.proc.execute".format(main.__name__))
        p2 = patch("{}.report_error".format(main.__name__))

        with p1 as proc_execute, p2 as report_error:
            proc_execute.side_effect = errors

            for err in errors:
                main.run(
                    cmd, timeout, shutdown, runner_log, ps_log,
                    stdout_log, stderr_log)

                self.assertTrue(proc_execute.called)
                self.assertTrue(report_error.called)
