"""A CLI for the package."""

import argparse
import sys

from . import log as cli_log
from ..lib import main


def parse_args(args):
    """Parse command line arguments."""
    desc = "Runs a CMD (it does no shell expansion)."
    parser = argparse.ArgumentParser(description=desc)

    cmd_help = "A cmd, e.g., (ls -la). NB: no shell expansion."
    parser.add_argument("CMD", help=cmd_help)

    timeout_help = "Num seconds before SIGTERM. Default: None"
    parser.add_argument(
        "--timeout", type=int, help=timeout_help, default=None)

    shutdown_help = "Num seconds from SIGTERM to SIGKILL. Default: 30"
    parser.add_argument(
        "--shutdown", type=int, help=shutdown_help, default=30)

    runner_log_help = "Where to send running info. Default: stdout. " + \
                      "Can also be stderr, /path/to/file.log, or /dev/null."
    parser.add_argument(
        "--runner-log", help=runner_log_help, default="stdout")

    runner_max_bytes_help = "Max bytes in log file before rotating."
    parser.add_argument(
        "--runner-log-max-bytes", type=int,
        help=runner_max_bytes_help, default=None)

    runner_max_files_help = "Max num of rotated files to keep."
    parser.add_argument(
        "--runner-log-max-files", type=int,
        help=runner_max_files_help, default=None)

    ps_log_help = "Where to send process info. Default: stdout. " + \
                  "Can also be stderr, /path/to/file.log, or /dev/null."
    parser.add_argument(
        "--ps-log", help=ps_log_help, default="stdout")

    ps_max_bytes_help = "Max bytes in log file before rotating."
    parser.add_argument(
        "--ps-log-max-bytes", type=int,
        help=ps_max_bytes_help, default=None)

    ps_max_files_help = "Max num of rotated files to keep."
    parser.add_argument(
        "--ps-log-max-files", type=int,
        help=ps_max_files_help, default=None)

    stdout_log_help = "Where to send CMD's stdout. Default: /dev/null. " + \
                      "Can also be stdout, stderr, or /path/to/file.log."
    parser.add_argument(
        "--stdout-log", help=stdout_log_help, default="/dev/null")

    stdout_max_bytes_help = "Max bytes in log file before rotating."
    parser.add_argument(
        "--stdout-log-max-bytes", type=int,
        help=stdout_max_bytes_help, default=None)

    stdout_max_files_help = "Max num of rotated files to keep."
    parser.add_argument(
        "--stdout-log-max-files", type=int,
        help=stdout_max_files_help, default=None)

    stderr_log_help = "Where to send CMD's stderr. Default: /dev/null. " + \
                      "Can also be stdout, stderr, or /path/to/file.log."
    parser.add_argument(
        "--stderr-log", help=stderr_log_help, default="/dev/null")

    stderr_max_bytes_help = "Max bytes in log file before rotating."
    parser.add_argument(
        "--stderr-log-max-bytes", type=int,
        help=stderr_max_bytes_help, default=None)

    stderr_max_files_help = "Max num of rotated files to keep."
    parser.add_argument(
        "--stderr-log-max-files", type=int,
        help=stderr_max_files_help, default=None)

    return parser.parse_args(args)


def get_log_or_exit(name, output, max_bytes, max_files):
    """Try to get a logger. Exit with a message if that fails."""
    try:
        log = cli_log.get_log(name, output, max_bytes, max_files)
    except OSError as e:
        sys.exit(str(e))
    return log


def cli():
    """Execute/run the CLI."""
    args = parse_args(sys.argv[1:])

    params = {}
    params["cmd"] = args.CMD
    params["timeout"] = args.timeout
    params["shutdown"] = args.shutdown

    runner_log = get_log_or_exit(
        "runner_log", args.runner_log,
        args.runner_log_max_bytes, args.runner_log_max_files)
    params["runner_log"] = runner_log

    ps_log = get_log_or_exit(
        "ps_log", args.ps_log,
        args.ps_log_max_bytes, args.ps_log_max_files)
    params["ps_log"] = ps_log

    stdout_log = get_log_or_exit(
        "stdout_log", args.stdout_log,
        args.stdout_log_max_bytes, args.stdout_log_max_files)
    params["stdout_log"] = stdout_log

    stderr_log = get_log_or_exit(
        "stderr_log", args.stderr_log,
        args.stderr_log_max_bytes, args.stderr_log_max_files)
    params["stderr_log"] = stderr_log

    try:
        main.run(**params)
    except:  # noqa: E722
        exc_type, exc_val, exc_tb = sys.exc_info()
        msg = "Error - {}: {}".format(exc_type.__name__, exc_val)
        sys.exit(msg)
