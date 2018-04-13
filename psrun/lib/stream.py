"""Execute/stream utilities."""

from queue import Queue, Empty
from threading import Thread


def put_lines_into_queue(stream, queue):
    """Read lines from a stream, put them on a queue, and close the stream.

    Args:

        stream
            A stream you can read lines from.

        queue
            A queue.

    Returns:
        The queue.
    """
    for line in iter(stream.readline, b''):
        queue.put(line)
    stream.close()
    return queue


def pop(queue):
    """Get the latest line on the queue, or ``None``.

    Args:

        queue
            A queue.

    Returns:
        The line, or ``None``.
    """
    try:
        return queue.get_nowait()
    except Empty:
        return None


def read(stream):
    """In a thread, read lines from a stream and put them on a queue.

    Args:

        stream
            The stream to read.

    Returns:
        A queue the lines can be popped from.
    """
    queue = Queue()
    thread = Thread(target=put_lines_into_queue, args=(stream, queue))
    thread.daemon = True
    thread.start()
    return queue
