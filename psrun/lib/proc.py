"""Utilities for executing a process."""

import datetime
import json
import subprocess
import sys
import time

from . import constants
from . import exceptions
from . import monitor
from . import stream


def try_monitor(log, pid):
    """Try to monitor a process, or report the error.

    Args:

        log
            A callable we can send info to.

        pid
            The pid of a process to monitor.

    """
    try:
        monitor.collect(log, pid)
    except:  # noqa: E722
        exc_type, exc_val, exc_tb = sys.exc_info()
        err_msg = "Error - {}: {}".format(exc_type.__name__, exc_val)
        data = {"pid": pid, "error": err_msg}
        log(json.dumps(data, sort_keys=True))


def read_buffer(buf, log):
    """Read all available lines from a buffer.

    Args:

        buf
            A buffer (queue) we can pop lines from.

        log
            A callable we can send each popped line to.

    """
    read_again = True
    while read_again:
        data = stream.pop(buf)
        if data:
            decoded_data = data.decode("utf8").rstrip()
            log(decoded_data)
        else:
            read_again = False


def start(cmd):
    """Start a process.

    Args:

        cmd
            A command to execute in the process, e.g., ["ls", "-la"].

    Raises:

        exceptions.PermissionDenied
            If permission to execute ``cmd`` is denied.

    Returns:
        A ``subprocess.Popen`` instance.

    """
    try:
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except PermissionError as e:
        msg = "Permission denied. Cannot execute: {}".format(" ".join(cmd))
        raise exceptions.PermissionDenied(msg)
    return p


def stop(p, shutdown):
    """Stop a process.

    Args:

        p
            A ``subprocess.Popen`` instance.

        shutdown
            The number of seconds to let the process shutdown.

    Returns:
        The exit code.

    """
    elapsed_time = 0
    p.terminate()

    do_again = True
    while do_again:
        if shutdown and elapsed_time > shutdown:
            p.kill()
            do_again = False
        else:
            exit_code = p.poll()
            do_again = exit_code is None
            time.sleep(constants.POLL_DELAY)
            elapsed_time = elapsed_time + constants.POLL_DELAY

    exit_code = p.poll()
    return exit_code


def do_again(p):
    """Check if we should poll again.

    Args:

        p
            A ``subprocess.Popen`` instance.

    Returns:
        ``True`` if we don't have an exit code yet. ``False`` otherwise.
    """
    exit_code = p.poll()
    return exit_code is None


def pause(p, elapsed_time):
    """Pause for a bit and increment the elapsed time.

    Args:

        p
            A ``subprocess.Popen`` instance.

        elapsed_time
            The number of seconds elapsed since the process started.

    Returns:
        The incremented elapsed time.
    """
    time.sleep(constants.POLL_DELAY)
    return elapsed_time + constants.POLL_DELAY


def raise_if_timeout(p, timeout, shutdown, elapsed_time, cmd):
    """Raise an error if the process has timed out.

    Args:

        p
            A ``subprocess.Popen`` instance.

        timeout
            The number of seconds to timeout, or ``None``.

        shutdown
            The number of seconds to let a process shutdown.

        elapsed_time
            The number of seconds elapsed since the process started.

        cmd
            The command executed in the process, e.g., ["ls", "-la"].

    Raises:

        exceptions.ProcTimeout
            If the process times out.

    """
    if timeout and elapsed_time > timeout:
        stop(p, shutdown)
        cmd_str = " ".join(cmd)
        msg = "Timed out after {} secs: {}".format(timeout, cmd_str)
        raise exceptions.ProcTimeout(msg)


def start_timing():
    """Start timing.

    Returns:
        The time this function was invoked.

    """
    start_time = datetime.datetime.now()
    return start_time


def stop_timing(start_time):
    """Stop timing and compute the running time since ``start_time``.

    Args:

        start_time
            The time the process started.

    Returns:
        The running time (in milliseconds).
    """
    end_time = datetime.datetime.now()
    total_seconds = (end_time - start_time).total_seconds()
    return int(total_seconds * 1000)


def execute(cmd, out, err, ps, timeout, shutdown):
    """Execute a command.

    Args:

        cmd
            A command to execute in the process, e.g., ["ls", "-la"].

        out
            A callable we can pass each line of stdout to.

        err
            A callable we can pass each line of stderr to.

        ps
            A callable we can pass stats about the proc to.

        timeout
            The number of seconds to timeout, or ``None``.

        shutdown
            The number of seconds to let a process shutdown.

    Returns:
        A tuple ``exit_code, running_time``.

    """
    elapsed_time = 0
    start_time = start_timing()

    p = start(cmd)

    stdout_buf = stream.read(p.stdout)
    stderr_buf = stream.read(p.stderr)

    while do_again(p):

        read_buffer(stdout_buf, out)
        read_buffer(stderr_buf, err)
        try_monitor(ps, p.pid)

        elapsed_time = pause(p, elapsed_time)

        raise_if_timeout(p, timeout, shutdown, elapsed_time, cmd)

    read_buffer(stdout_buf, out)
    read_buffer(stderr_buf, err)
    try_monitor(ps, p.pid)

    running_time = stop_timing(start_time)
    exit_code = p.poll()
    return exit_code, running_time
