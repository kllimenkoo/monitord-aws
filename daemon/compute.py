from models import (
    CpuRawData,
    DiskMetrics,
    DiskRawData,
    NetMetrics,
    NetRawData,
    RamMetrics,
    RamRawData,
)


def compute_cpu_metrics(prev: CpuRawData, curr: CpuRawData) -> float | None:
    prev_idle = prev.idle + prev.iowait
    curr_idle = curr.idle + curr.iowait

    prev_total = sum(prev.total)
    curr_total = sum(curr.total)

    delta_idle = curr_idle - prev_idle
    delta_total = curr_total - prev_total

    if delta_total == 0:
        return None

    cpu_usage_percent = 100 * (1 - (delta_idle / delta_total))
    return cpu_usage_percent


def compute_ram_metrics(snapshot: RamRawData) -> RamMetrics:
    if snapshot.mem_total == 0:
        raise ValueError('mem_total is 0 - /proc/meminfo may be corrupted.')

    mem_usage_percentage = 100 * (1 - (snapshot.mem_available / snapshot.mem_total))

    if snapshot.swap_total > 0:
        swap_usage_percentage = 100 * (1 - (snapshot.swap_free / snapshot.swap_total))
    else:
        swap_usage_percentage = 0.0

    return RamMetrics(
        mem_usage_percentage=mem_usage_percentage,
        swap_usage_percentage=swap_usage_percentage,
    )


def compute_disk_metrics(
    prev: dict[str, DiskRawData], curr: dict[str, DiskRawData], interval: float
) -> dict[str, DiskMetrics]:
    result = {}
    for name, curr_stats in curr.items():
        if name not in prev:
            continue

        if interval == 0:
            continue

        prev_stats = prev[name]

        delta_io_time = curr_stats.io_time_spent - prev_stats.io_time_spent

        io_utilization_percentage = 100 * (
            delta_io_time / (interval * 1000)
        )  # interval to ms

        result[name] = DiskMetrics(
            io_utilization_percentage=io_utilization_percentage,
        )

    return result


def compute_net_metrics(
    prev: dict[str, NetRawData], curr: dict[str, NetRawData], interval: float
) -> dict[str, NetMetrics]:
    result = {}
    for name, curr_stats in curr.items():
        if name not in prev:
            continue

        if interval == 0:
            continue

        prev_stats = prev[name]

        delta_receive_bytes = curr_stats.receive_bytes - prev_stats.receive_bytes
        delta_transmit_bytes = curr_stats.transmit_bytes - prev_stats.transmit_bytes

        receive_bytes_per_sec = delta_receive_bytes / interval
        transmit_bytes_per_sec = delta_transmit_bytes / interval

        receive_packet_error_count = (
            curr_stats.receive_errors - prev_stats.receive_errors
        )
        receive_packet_drop_count = curr_stats.receive_drops - prev_stats.receive_drops
        transmit_packet_error_count = (
            curr_stats.transmit_errors - prev_stats.transmit_errors
        )
        transmit_packet_drop_count = (
            curr_stats.transmit_drops - prev_stats.transmit_drops
        )

        result[name] = NetMetrics(
            receive_bytes_per_sec=receive_bytes_per_sec,
            receive_packet_error_count=receive_packet_error_count,
            receive_packet_drop_count=receive_packet_drop_count,
            transmit_bytes_per_sec=transmit_bytes_per_sec,
            transmit_packet_error_count=transmit_packet_error_count,
            transmit_packet_drop_count=transmit_packet_drop_count,
        )

    return result
