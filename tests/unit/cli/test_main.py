"""Unit tests for the ``cli.main`` module."""

from unittest import TestCase
from unittest.mock import patch, Mock

from psrun.cli import main


class TestMain(TestCase):
    """Test suite for the ``cli.main`` module."""

    def test_parse_args(self):
        """Ensure ``parse_args()`` parses the correct args."""
        cmd = "cmd -al"
        timeout = "60"
        shutdown = "10"
        args = [
            cmd, "--timeout", timeout, "--shutdown", shutdown,
            "--runner-log", "stdout", "--runner-log-max-bytes", "1000",
            "--runner-log-max-file", "4",
            "--ps-log", "stdout", "--ps-log-max-bytes", "1000",
            "--ps-log-max-file", "4",
            "--stdout-log", "stdout", "--stdout-log-max-bytes", "1000",
            "--stdout-log-max-files", "4",
            "--stderr-log", "stderr",
            "--stderr-log-max-bytes", "1000", "--stderr-log-max-files", "4"]
        result = main.parse_args(args)
        self.assertEqual(result.CMD, cmd)
        self.assertEqual(result.timeout, int(timeout))
        self.assertEqual(result.shutdown, int(shutdown))
        self.assertEqual(result.runner_log, "stdout")
        self.assertEqual(result.runner_log_max_bytes, 1000)
        self.assertEqual(result.runner_log_max_files, 4)
        self.assertEqual(result.ps_log, "stdout")
        self.assertEqual(result.ps_log_max_bytes, 1000)
        self.assertEqual(result.ps_log_max_files, 4)
        self.assertEqual(result.stdout_log, "stdout")
        self.assertEqual(result.stdout_log_max_bytes, 1000)
        self.assertEqual(result.stdout_log_max_files, 4)
        self.assertEqual(result.stderr_log, "stderr")
        self.assertEqual(result.stderr_log_max_bytes, 1000)
        self.assertEqual(result.stderr_log_max_files, 4)

    def test_get_log_or_exit(self):
        """Ensure ``test_get_log_or_exit()`` returns a log."""
        log = Mock()
        args = ["name", "stream", 1000, 4]

        p = patch("{}.cli_log.get_log".format(main.__name__))
        with p as get_log:
            get_log.return_value = log
            result = main.get_log_or_exit(*args)
            self.assertEqual(result, log)
            get_log.assert_called_once_with(*args)

    def test_get_log_or_exit_with_error(self):
        """Ensure ``test_get_log_or_exit()`` exits on error."""
        args = ["name", "stream", 1000, 4]

        p = patch("{}.cli_log.get_log".format(main.__name__))
        with p as get_log:
            get_log.side_effect = OSError
            with self.assertRaises(SystemExit):
                main.get_log_or_exit(*args)

    def test_cli(self):
        """Ensure ``cli()`` invokes the main program."""
        runner_log = Mock()
        ps_log = Mock()
        stdout_log = Mock()
        stderr_log = Mock()

        args = Mock(
            CMD="cmd -al", timeout=None, shutdown=30, runner_log=runner_log,
            ps_log=ps_log, stdout_log=stdout_log, stderr_log=stderr_log)

        p1 = patch("{}.parse_args".format(main.__name__))
        p2 = patch("{}.cli_log.get_log".format(main.__name__))
        p3 = patch("{}.main.run".format(main.__name__))
        with p1 as parse_args, p2 as get_log, p3 as main_run:
            parse_args.return_value = args
            get_log.side_effect = [runner_log, ps_log, stdout_log, stderr_log]

            main.cli()
            main_run.assert_called_once_with(
                cmd=args.CMD, timeout=args.timeout, shutdown=args.shutdown,
                runner_log=args.runner_log, ps_log=args.ps_log,
                stdout_log=args.stdout_log, stderr_log=args.stderr_log)

    def test_cli_catches_main_errors(self):
        """Ensure ``cli()`` catches ``run()`` errors."""
        args = Mock(CMD="cmd -al")
        log = Mock()
        p1 = patch("{}.parse_args".format(main.__name__))
        p2 = patch("{}.cli_log.get_log".format(main.__name__))
        p3 = patch("{}.main.run".format(main.__name__))
        with p1 as parse_args, p2 as get_log, p3 as main_run:
            parse_args.return_value = args
            get_log.return_value = log
            main_run.side_effect = Exception
            with self.assertRaises(SystemExit):
                main.cli()
