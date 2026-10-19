import asyncio
import statistics

from models import Alert
from storage import (
    get_known_devices,
    get_known_interfaces,
    read_cpu,
    read_disk,
    read_net,
    read_ram,
    write_alert,
)

CPU_SHORT_WINDOW, CPU_LONG_WINDOW = 5, 20
CPU_SENSITIVITY = 2.0
CPU_STDEV_FLOOR = 0.5

RAM_SHORT_WINDOW, RAM_LONG_WINDOW = 5, 20
RAM_SENSITIVITY = 2.0
RAM_STDEV_FLOOR = 0.5

DISK_SHORT_WINDOW, DISK_LONG_WINDOW = 10, 20
DISK_SENSITIVITY = 2.0
DISK_STDEV_FLOOR = 0.5

NET_SHORT_WINDOW, NET_LONG_WINDOW = 8, 20
NET_SENSITIVITY = 2.0
NET_STDEV_FLOOR = 500.0


async def check_cpu() -> None:
    long_window = await read_cpu(limit=CPU_LONG_WINDOW)
    if len(long_window) < CPU_LONG_WINDOW:
        return None

    short_window = long_window[:CPU_SHORT_WINDOW]
    baseline_window = long_window[CPU_SHORT_WINDOW:]

    short_values = [m['usage_percentage'] for m in short_window]
    baseline_values = [m['usage_percentage'] for m in baseline_window]

    avg_short = statistics.mean(short_values)
    avg_long = statistics.mean(baseline_values)

    long_stdev = max(statistics.stdev(baseline_values), CPU_STDEV_FLOOR)
    adaptive_threshold = avg_long + (CPU_SENSITIVITY * long_stdev)

    if avg_short > adaptive_threshold:
        await write_alert(
            Alert(
                metric='cpu',
                device=None,
                avg_short=avg_short,
                avg_long=avg_long,
                threshold=adaptive_threshold,
            )
        )


async def check_ram() -> None:
    long_window = await read_ram(limit=RAM_LONG_WINDOW)
    if len(long_window) < RAM_LONG_WINDOW:
        return None

    short_window = long_window[:RAM_SHORT_WINDOW]
    baseline_window = long_window[RAM_SHORT_WINDOW:]

    short_values_mem = [m['mem_usage_percentage'] for m in short_window]
    baseline_values_mem = [m['mem_usage_percentage'] for m in baseline_window]

    avg_short_mem = statistics.mean(short_values_mem)
    avg_long_mem = statistics.mean(baseline_values_mem)

    long_stdev_mem = max(statistics.stdev(baseline_values_mem), RAM_STDEV_FLOOR)
    adaptive_threshold_mem = avg_long_mem + (RAM_SENSITIVITY * long_stdev_mem)

    short_values_swap = [m['swap_usage_percentage'] for m in short_window]
    baseline_values_swap = [m['swap_usage_percentage'] for m in baseline_window]

    avg_short_swap = statistics.mean(short_values_swap)
    avg_long_swap = statistics.mean(baseline_values_swap)

    long_stdev_swap = max(statistics.stdev(baseline_values_swap), RAM_STDEV_FLOOR)
    adaptive_threshold_swap = avg_long_swap + (RAM_SENSITIVITY * long_stdev_swap)

    if avg_short_mem > adaptive_threshold_mem:
        await write_alert(
            Alert(
                metric='ram',
                device=None,
                avg_short=avg_short_mem,
                avg_long=avg_long_mem,
                threshold=adaptive_threshold_mem,
            )
        )

    if avg_short_swap > adaptive_threshold_swap:
        await write_alert(
            Alert(
                metric='ram',
                device=None,
                avg_short=avg_short_swap,
                avg_long=avg_long_swap,
                threshold=adaptive_threshold_swap,
            )
        )


async def check_disk() -> None:
    devices = await get_known_devices()
    for item in devices:
        device = item['device']
        long_window = await read_disk(device=device, limit=DISK_LONG_WINDOW)
        if len(long_window) < DISK_LONG_WINDOW:
            continue

        short_window = long_window[:DISK_SHORT_WINDOW]
        baseline_window = long_window[DISK_SHORT_WINDOW:]

        short_values = [m['io_utilization_percentage'] for m in short_window]
        baseline_values = [m['io_utilization_percentage'] for m in baseline_window]

        avg_short = statistics.mean(short_values)
        avg_long = statistics.mean(baseline_values)

        long_stdev = max(statistics.stdev(baseline_values), DISK_STDEV_FLOOR)
        adaptive_threshold = avg_long + (DISK_SENSITIVITY * long_stdev)

        if avg_short > adaptive_threshold:
            await write_alert(
                Alert(
                    metric='disk',
                    device=device,
                    avg_short=avg_short,
                    avg_long=avg_long,
                    threshold=adaptive_threshold,
                )
            )


async def check_net() -> None:
    interfaces = await get_known_interfaces()
    for item in interfaces:
        interface = item['interface']
        long_window = await read_net(interface=interface, limit=NET_LONG_WINDOW)
        if len(long_window) < NET_LONG_WINDOW:
            continue

        short_window = long_window[:NET_SHORT_WINDOW]
        baseline_window = long_window[NET_SHORT_WINDOW:]

        short_values_receive = [m['receive_bytes_per_sec'] for m in short_window]
        baseline_values_receive = [m['receive_bytes_per_sec'] for m in baseline_window]

        avg_short_receive = statistics.mean(short_values_receive)
        avg_long_receive = statistics.mean(baseline_values_receive)

        long_stdev_receive = max(
            statistics.stdev(baseline_values_receive), NET_STDEV_FLOOR
        )
        adaptive_threshold_receive = avg_long_receive + (
            NET_SENSITIVITY * long_stdev_receive
        )

        short_values_transmit = [m['transmit_bytes_per_sec'] for m in short_window]
        baseline_values_transmit = [
            m['transmit_bytes_per_sec'] for m in baseline_window
        ]

        avg_short_transmit = statistics.mean(short_values_transmit)
        avg_long_transmit = statistics.mean(baseline_values_transmit)

        long_stdev_transmit = max(
            statistics.stdev(baseline_values_transmit), NET_STDEV_FLOOR
        )
        adaptive_threshold_transmit = avg_long_transmit + (
            NET_SENSITIVITY * long_stdev_transmit
        )

        if avg_short_receive > adaptive_threshold_receive:
            await write_alert(
                Alert(
                    metric='network',
                    device=interface,
                    avg_short=avg_short_receive,
                    avg_long=avg_long_receive,
                    threshold=adaptive_threshold_receive,
                )
            )

        if avg_short_transmit > adaptive_threshold_transmit:
            await write_alert(
                Alert(
                    metric='network',
                    device=interface,
                    avg_short=avg_short_transmit,
                    avg_long=avg_long_transmit,
                    threshold=adaptive_threshold_transmit,
                )
            )


async def run_anomaly_checks() -> None:
    while True:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(check_cpu())
            tg.create_task(check_ram())
            tg.create_task(check_disk())
            tg.create_task(check_net())
        await asyncio.sleep(5)
