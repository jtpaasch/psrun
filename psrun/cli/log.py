"""Log utilities for the CLI."""

import logging
import logging.handlers

import sys

from collections import OrderedDict

fmt = "%(message)s"
"""A format for log messages."""


def get_writer(func):
    """Return a function that applies a func to an arg."""
    def wrapper(msg):
        func(msg)
    return wrapper


def get_null_logger(name):
    """Get a null logger.

    Args:

        name
            A name for the logger.

    Returns:
        A null logger.

    """
    handler = logging.NullHandler()
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def get_stream_logger(name, stream):
    """Get a stream logger.

    Args:

        name
            A name for the logger.

        stream
            A stream to log to, e.g., ``sys.stdout``.

    Returns:
        A stream logger.

    """
    formatter = logging.Formatter(fmt)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def get_file_logger(name, path, num_bytes=None, num_files=None):
    """Get a file logger.

    Args:

        name
            A name for the logger.

        path
            A path to write to.

        num_bytes
            Number of bytes to write in a file before rotating.

        num_files
            Number of files to keep.

    Returns:
        A file logger.

    """
    params = OrderedDict()
    params.update({"filename": path})
    if num_bytes:
        params.update({"maxBytes": num_bytes})
    if num_files:
        params.update({"backupCount": num_files})
    formatter = logging.Formatter(fmt)
    handler = logging.handlers.RotatingFileHandler(**params)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def get_log(name, output, num_bytes=None, num_files=None):
    """Get a file logger.

    Args:

        name
            A name for the logger.

        output
            Where to write log messages to. The value should be a string:
            "/dev/null", "stdout", "stderr", or a path like "/dummy/path".

        num_bytes
            Number of bytes to write in a file before rotating.

        num_files
            Number of files to keep.

    Returns:
        A function you can send messages to.

    """
    logger = None
    if output == "/dev/null":
        logger = get_null_logger(name)
    elif output == "stdout":
        logger = get_stream_logger(name, sys.stdout)
    elif output == "stderr":
        logger = get_stream_logger(name, sys.stderr)
    else:
        logger = get_file_logger(name, output, num_bytes, num_files)
    return get_writer(logger.info)
