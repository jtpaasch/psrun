"""Unit tests for the ``lib.monitor`` module."""

from unittest import TestCase
from unittest.mock import patch, Mock

import json

from psrun.lib import monitor


class TestMonitor(TestCase):
    """Test suite for the ``lib.monitor`` module."""

    def test_collect(self):
        """Ensure ``collect()`` logs the right structured data."""
        pid = 10
        pids = [1, 2, 10]
        cpu_count = "dummy-cpu-count"
        cpu_times = Mock(user="user", system="system", idle="idle")
        cpu_stats = Mock(
            ctx_switches="ctx_switches", interrupts="interrupts",
            soft_interrupts="soft_interrupts", syscalls="syscalls")
        cpu_freq = Mock(current="current", min="min", max="max")
        virtual_memory = Mock(
            total="total", available="available", used="used", free="free")
        swap_memory = Mock(
            total="total", used="used", free="free", percent="percent",
            sin="sin", sout="sout")

        expected_data = {
            "all_pids": pids,
            "cpu_count": "dummy-cpu-count",
            "cpu_freq": {"current": "current", "max": "max", "min": "min"},
            "cpu_freq_per_cpu": [
                {"current": "current", "max": "max", "min": "min"},
                {"current": "current", "max": "max", "min": "min"}],
            "cpu_stats": {
                "ctx_switches": "ctx_switches", "interrupts": "interrupts",
                "soft_interrupts": "soft_interrupts",
                "syscalls": "syscalls"},
            "cpu_times": {"idle": "idle", "system": "system", "user": "user"},
            "cpu_times_per_cpu": [
                {"idle": "idle", "system": "system", "user": "user"},
                {"idle": "idle", "system": "system", "user": "user"}],
            "pid": pid,
            "swap_memory": None,
            "virtual_memory": {
                "available": "available", "free": "free", "total": "total",
                "used": "used"}
        }
        expected = json.dumps(expected_data, sort_keys=True)

        data = []
        log = data.append

        p1 = patch("{}.psutil".format(monitor.__name__))
        with p1 as psutil:

            psutil.pids = Mock()
            psutil.pids.return_value = pids

            psutil.cpu_count = Mock()
            psutil.cpu_count.return_value = cpu_count

            psutil.cpu_times = Mock()
            psutil.cpu_times.side_effect = [cpu_times, [cpu_times, cpu_times]]

            psutil.cpu_stats = Mock()
            psutil.cpu_stats.return_value = cpu_stats

            psutil.cpu_freq = Mock()
            psutil.cpu_freq.side_effect = [
                cpu_freq, [cpu_freq, cpu_freq],
                cpu_freq, [cpu_freq, cpu_freq]]

            psutil.virtual_memory = Mock()
            psutil.virtual_memory.return_value = virtual_memory

            psutil.swap_memory = Mock()
            psutil.swap_memory.return_value = swap_memory

            monitor.collect(log, pid)

            self.assertEqual(data[0], expected)
