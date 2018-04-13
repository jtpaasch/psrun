"""The main module for the package."""

from . import exceptions
from . import proc


def report_start_details(log, cmd):
    """Pass starting details to a ``log()`` function.

    Args:

        log
            A callable we can send messages to.

        cmd
            A command to report about, e.g., 'ls -la'.

    """
    log("-- ------------------------")
    log("-- Executing {} ...".format(cmd))


def report_final_details(log, exit_code, running_time):
    """Pass final details to a ``log()`` function.

    Args:

        log
            A callable we can send messages to.

        exit_code
            The exit code of the process.

        running_time
            The time the process took to run.

    """
    log("-- Exit code: {}".format(exit_code))
    log("-- Run time: {}ms".format(running_time))


def report_error(log, error):
    """Pass error info to a ``log()`` function.

    Args:

        log
            A callable we can send messages to.

        error
            The error to report.

    """
    log("-- ERROR: {}".format(error))


def run(cmd, timeout, shutdown, runner_log, ps_log, stdout_log, stderr_log):
    """Execute a command.

    Args:

        cmd
            A command to execute, e.g., 'ls -la'.

        timeout
            The number of seconds to timeout, or ``None``.

        shutdown
            The number of seconds to let a process shutdown.

        runner_log
            A callable we can send messages from the runner to.

        ps_log
            A callable we can send info about the process to.

        stdout_log
            A callable we can send lines from stdout to.

        stderr_log
            A callable we can send lines from stderr to.

    """
    errs = (exceptions.ProcTimeout, exceptions.PermissionDenied)
    report_start_details(runner_log, cmd)
    try:
        exit_code, running_time = proc.execute(
            cmd, stdout_log, stderr_log, ps_log, timeout, shutdown)
    except errs as error:
        report_error(runner_log, error)
    else:
        report_final_details(runner_log, exit_code, running_time)
