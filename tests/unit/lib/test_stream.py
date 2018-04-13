"""Unit tests for the ``lib.stream`` module."""

from unittest import TestCase
from queue import Queue
import io

from psrun.lib import stream as stream_lib


class TestStream(TestCase):
    """Test suite for the ``lib.stream`` module."""

    def test_pop(self):
        """Ensure ``pop()`` pops the latest line on a queue."""
        q = Queue()
        line = b"dummy line\n"
        q.put(line)
        result = stream_lib.pop(q)
        self.assertEqual(result, line)

    def test_pop_with_no_lines(self):
        """Ensure ``pop()`` returns ``None`` if the queue is empty."""
        q = Queue()
        result = stream_lib.pop(q)
        self.assertIsNone(result)

    def test_read(self):
        """Ensure ``read()`` reads in a thread and returns a queue."""
        lines = [b"line 1\n", b"line 2\n", b"line 3\n"]
        out = b"".join(lines)
        stream = io.BytesIO(out)

        result = stream_lib.read(stream)
        for line in lines:
            self.assertEqual(line, result.get())
        self.assertTrue(result.empty())
