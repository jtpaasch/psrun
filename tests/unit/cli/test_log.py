"""Unit tests for the ``main.cli`` module."""

from unittest import TestCase
from unittest.mock import Mock, patch

import io
import os
import sys

import logging
import logging.handlers

from collections import OrderedDict

from psrun.cli import log as log_lib


class TestLog(TestCase):
    """Test suite for the ``main.cli`` module."""

    def test_get_writer(self):
        """Ensure ``get_writer()`` returns a wrapper."""
        data = []
        wrapper = log_lib.get_writer(data.append)
        wrapper("dummy-data")
        self.assertEqual(data[0], "dummy-data")

    def test_get_null_logger(self):
        """Ensure ``get_null_logger()`` builds a null logger."""
        name = "dummy-name"
        handler = logging.NullHandler()
        p = patch("{}.logging.NullHandler".format(log_lib.__name__))
        with p as NullHandler:
            NullHandler.return_value = handler
            log_lib.get_null_logger(name)
            self.assertTrue(NullHandler.called)

    def test_get_stream_logger(self):
        """Ensure ``get_stream_logger()`` builds a stream logger."""
        name = "dummy-name"
        stream = io.StringIO()
        logger = log_lib.get_stream_logger(name, stream)
        msg = "dummy message"
        logger.info(msg)
        result = stream.getvalue()
        self.assertEqual(result, "{}{}".format(msg, os.linesep))

    def test_get_file_logger(self):
        """Ensure ``get_file_logger()`` builds a rotating file handler."""
        name = "dummy-name"
        path = "/dummy/path"
        num_bytes = 1000
        num_files = 4
        msg = "dummy message"

        params = OrderedDict()
        params.update({"filename": path})
        params.update({"maxBytes": num_bytes})
        params.update({"backupCount": num_files})

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        log_module = log_lib.__name__
        p = patch(
            "{}.logging.handlers.RotatingFileHandler".format(log_module))
        with p as Handler:
            Handler.return_value = handler

            logger = log_lib.get_file_logger(name, path, num_bytes, num_files)
            logger.info(msg)

            Handler.assert_called_once_with(**params)
            result = stream.getvalue()
            self.assertEqual(result, "{}{}".format(msg, os.linesep))

    def test_get_file_logger_with_no_options(self):
        """Ensure ``get_file_logger()`` handles no rotation options."""
        name = "dummy-name"
        path = "/dummy/path"
        msg = "dummy message"

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        log_module = log_lib.__name__
        p = patch(
            "{}.logging.handlers.RotatingFileHandler".format(log_module))
        with p as Handler:
            Handler.return_value = handler

            logger = log_lib.get_file_logger(name, path)
            logger.info(msg)

            Handler.assert_called_once_with(filename=path)
            result = stream.getvalue()
            self.assertEqual(result, "{}{}".format(msg, os.linesep))

    def test_get_null_log(self):
        """Ensure ``get_log()`` dispatches to null log builders."""
        name = "dummy-name"
        output = "/dev/null"
        logger = Mock(info=Mock())
        writer = Mock()

        p1 = patch("{}.get_null_logger".format(log_lib.__name__))
        p2 = patch("{}.get_writer".format(log_lib.__name__))

        with p1 as get_null_logger, p2 as get_writer:
            get_null_logger.return_value = logger
            get_writer.return_value = writer

            result = log_lib.get_log(name, output)

            self.assertEqual(result, writer)
            get_null_logger.assert_called_once_with(name)
            get_writer.assert_called_once_with(logger.info)

    def test_get_stdout_log(self):
        """Ensure ``get_log()`` dispatches to stdout log builders."""
        name = "dummy-name"
        output = "stdout"
        logger = Mock(info=Mock())
        writer = Mock()

        p1 = patch("{}.get_stream_logger".format(log_lib.__name__))
        p2 = patch("{}.get_writer".format(log_lib.__name__))

        with p1 as get_stream_logger, p2 as get_writer:
            get_stream_logger.return_value = logger
            get_writer.return_value = writer

            result = log_lib.get_log(name, output)

            self.assertEqual(result, writer)
            get_stream_logger.assert_called_once_with(name, sys.stdout)
            get_writer.assert_called_once_with(logger.info)

    def test_get_stderr_log(self):
        """Ensure ``get_log()`` dispatches to stderr log builders."""
        name = "dummy-name"
        output = "stderr"
        logger = Mock(info=Mock())
        writer = Mock()

        p1 = patch("{}.get_stream_logger".format(log_lib.__name__))
        p2 = patch("{}.get_writer".format(log_lib.__name__))

        with p1 as get_stream_logger, p2 as get_writer:
            get_stream_logger.return_value = logger
            get_writer.return_value = writer

            result = log_lib.get_log(name, output)

            self.assertEqual(result, writer)
            get_stream_logger.assert_called_once_with(name, sys.stderr)
            get_writer.assert_called_once_with(logger.info)

    def test_get_file_log(self):
        """Ensure ``get_log()`` dispatches to file log builders."""
        name = "dummy-name"
        output = "/dummy/path"
        num_bytes = 1000
        num_files = 4
        logger = Mock(info=Mock())
        writer = Mock()

        p1 = patch("{}.get_file_logger".format(log_lib.__name__))
        p2 = patch("{}.get_writer".format(log_lib.__name__))

        with p1 as get_file_logger, p2 as get_writer:
            get_file_logger.return_value = logger
            get_writer.return_value = writer

            result = log_lib.get_log(name, output, num_bytes, num_files)

            self.assertEqual(result, writer)
            get_file_logger.assert_called_once_with(
                name, output, num_bytes, num_files)
            get_writer.assert_called_once_with(logger.info)
