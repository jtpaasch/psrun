"""Utilities for monitoring a process."""

import json
import psutil


def cpu_times():
    """Get system CPU times."""
    data = {}
    cpu_times = psutil.cpu_times()
    data["user"] = cpu_times.user
    data["system"] = cpu_times.system
    data["idle"] = cpu_times.idle
    return data


def cpu_times_per_cpu():
    """Get system CPU times, per CPU."""
    data = []
    cpu_times = psutil.cpu_times(percpu=True)
    for cpu in cpu_times:
        record = {}
        record["user"] = cpu.user
        record["system"] = cpu.system
        record["idle"] = cpu.idle
        data.append(record)
    return data


def cpu_stats():
    """Get CPU stats."""
    data = {}
    stats = psutil.cpu_stats()
    data["ctx_switches"] = stats.ctx_switches
    data["interrupts"] = stats.interrupts
    data["soft_interrupts"] = stats.soft_interrupts
    data["syscalls"] = stats.syscalls
    return data


def cpu_freq():
    """Get CPU frequency."""
    data = {}
    freq = psutil.cpu_freq()
    data["current"] = freq.current
    data["min"] = freq.min
    data["max"] = freq.max
    return data


def cpu_freq_per_cpu():
    """Get CPU frequency per CPU."""
    data = []
    freq = psutil.cpu_freq(percpu=True)
    for fr in freq:
        record = {}
        record["current"] = fr.current
        record["min"] = fr.min
        record["max"] = fr.max
        data.append(record)
    return data


def virtual_memory():
    """Get virtual memory info."""
    data = {}
    vm = psutil.virtual_memory()
    data["total"] = vm.total
    data["available"] = vm.available
    data["used"] = vm.used
    data["free"] = vm.free
    return data


def swap_memory():
    """Get swap memory info."""
    data = {}
    swap = psutil.swap_memory()
    data["total"] = swap.total
    data["used"] = swap.used
    data["free"] = swap.free
    data["percent"] = swap.percent
    data["sin"] = swap.sin
    data["sout"] = swap.sout


def collect(log, pid):
    """Collect stats about a process."""
    data = {}

    data["pid"] = pid
    data["all_pids"] = psutil.pids()

    data["cpu_count"] = psutil.cpu_count()
    data["cpu_freq"] = cpu_freq()
    data["cpu_freq_per_cpu"] = cpu_freq_per_cpu()
    data["cpu_times"] = cpu_times()
    data["cpu_times_per_cpu"] = cpu_times_per_cpu()
    data["cpu_stats"] = cpu_stats()
    data["cpu_freq"] = cpu_freq()
    data["cpu_freq_per_cpu"] = cpu_freq_per_cpu()

    data["virtual_memory"] = virtual_memory()
    data["swap_memory"] = swap_memory()

    serialized_data = json.dumps(data, sort_keys=True)
    log(serialized_data)
