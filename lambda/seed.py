import math
import random
import sqlite3
import time
from pathlib import Path as FilePath

DEMO_DB = FilePath(__file__).parent / 'demo.db'


def populate(cur: sqlite3.Cursor):
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS cpu_metrics(
            timestamp REAL,
            usage_percentage REAL
        );
        CREATE TABLE IF NOT EXISTS ram_metrics(
            timestamp REAL,
            mem_usage_percentage REAL,
            swap_usage_percentage REAL
        );
        CREATE TABLE IF NOT EXISTS disk_metrics(
            timestamp REAL,
            device TEXT,
            read_iops REAL,
            read_bytes_per_sec REAL,
            write_iops REAL,
            write_bytes_per_sec REAL,
            io_utilization_percentage REAL
        );
        CREATE TABLE IF NOT EXISTS net_metrics(
            timestamp REAL,
            interface TEXT,
            receive_bytes_per_sec REAL,
            receive_packets_per_sec REAL,
            transmit_bytes_per_sec REAL,
            transmit_packets_per_sec REAL,
            receive_packet_error_count REAL,
            receive_packet_drop_count REAL,
            transmit_packet_error_count REAL,
            transmit_packet_drop_count REAL
        );
        """)

    records = 150
    now = time.time()
    for i in range(records, 0, -1):
        ts = now - i

        cur.execute(
            'INSERT INTO cpu_metrics VALUES (?, ?)',
            (ts, round(35 + 25 * math.sin(i / 20) + random.uniform(0, 1), 2)),
        )

        cur.execute(
            'INSERT INTO ram_metrics VALUES (?, ?, ?)',
            (ts, round(50 + 25 * math.sin(i / 20) + random.uniform(0, 1), 2), 0),
        )

        for device in ('sda', 'sdb'):
            cur.execute(
                'INSERT INTO disk_metrics VALUES (?, ?, ?, ?, ?, ?, ?)',
                (
                    ts,
                    device,
                    random.uniform(100, 300),
                    random.uniform(1e6, 5e6),
                    random.uniform(100, 300),
                    random.uniform(1e6, 5e6),
                    round(10 + 10 * math.sin(i / 20) + random.uniform(0, 1), 2),
                ),
            )

        for interface in ('eth0', 'enp0s3'):
            cur.execute(
                'INSERT INTO net_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    ts,
                    interface,
                    random.uniform(1e4, 5e6),
                    random.uniform(100, 300),
                    random.uniform(1e3, 3e6),
                    random.uniform(100, 300),
                    0,
                    0,
                    0,
                    0,
                ),
            )


if __name__ == '__main__':
    con = sqlite3.connect(DEMO_DB)
    cur = con.cursor()
    populate(cur)
    con.commit()
    con.close()
