from typing import NamedTuple


class CpuRawData(NamedTuple):
    """Holds raw data read from /proc/stat"""

    idle: int
    iowait: int
    total: list[int]


class CpuMetrics(NamedTuple):
    """Holds calculated data from CPU"""

    usage_percentage: float


class RamRawData(NamedTuple):
    """Holds raw data read from /proc/meminfo."""

    mem_total: int
    mem_available: int
    swap_total: int
    swap_free: int


class RamMetrics(NamedTuple):
    """Holds calculated data from RAM."""

    mem_usage_percentage: float
    swap_usage_percentage: float


class DiskRawData(NamedTuple):
    """Holds raw data read from /proc/diskstats."""

    io_time_spent: int


class DiskMetrics(NamedTuple):
    """Holds calculated data from disk read."""

    io_utilization_percentage: float


class NetRawData(NamedTuple):
    """Holds raw data read from /proc/net/dev."""

    receive_bytes: int
    receive_errors: int
    receive_drops: int
    transmit_bytes: int
    transmit_errors: int
    transmit_drops: int


class NetMetrics(NamedTuple):
    """Holds calculated data from network read."""

    receive_bytes_per_sec: float
    receive_packet_error_count: int
    receive_packet_drop_count: int
    transmit_bytes_per_sec: float
    transmit_packet_error_count: int
    transmit_packet_drop_count: int


class Alert(NamedTuple):
    """Holds alerts after anomaly was detected"""

    metric: str
    device: str | None
    avg_short: float
    avg_long: float
    threshold: float
