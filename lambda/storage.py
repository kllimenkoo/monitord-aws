import time
from decimal import Decimal

import aioboto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from models import Alert, DiskMetrics, NetMetrics, RamMetrics
from tables import (
    ALERTS_TABLE,
    CPU_TABLE,
    DISK_TABLE,
    KNOWN_DEVICES_TABLE,
    KNOWN_INTERFACES_TABLE,
    NET_TABLE,
    RAM_TABLE,
)

_resource = None


async def get_resource():
    global _resource
    if _resource is None:
        session = aioboto3.Session()
        _resource = await session.resource('dynamodb').__aenter__()
    return _resource


async def init_db() -> None:
    db = await get_resource()
    for table_def in [
        CPU_TABLE,
        RAM_TABLE,
        DISK_TABLE,
        NET_TABLE,
        ALERTS_TABLE,
        KNOWN_DEVICES_TABLE,
        KNOWN_INTERFACES_TABLE,
    ]:
        try:
            await db.create_table(**table_def)
        except ClientError as e:
            if e.response.get('Error', {}).get('Code', {}) == 'ResourceInUseException':
                pass
            else:
                raise


async def write_cpu(usage_percentage: float | None) -> None:
    db = await get_resource()
    table = await db.Table('cpu_metrics')
    await table.put_item(
        Item={
            'metric': 'cpu',
            'timestamp': Decimal(str(time.time())),
            'usage_percentage': Decimal(str(usage_percentage)),
        }
    )


async def write_ram(metrics: RamMetrics) -> None:
    db = await get_resource()
    table = await db.Table('ram_metrics')
    await table.put_item(
        Item={
            'metric': 'ram',
            'timestamp': Decimal(str(time.time())),
            'mem_usage_percentage': Decimal(str(metrics.mem_usage_percentage)),
            'swap_usage_percentage': Decimal(str(metrics.swap_usage_percentage)),
        }
    )


async def write_disk(metrics: dict[str, DiskMetrics]) -> None:
    db = await get_resource()
    table = await db.Table('disk_metrics')
    for device, dev_metrics in metrics.items():
        await table.put_item(
            Item={
                'metric': 'disk',
                'dev_name': device,
                'timestamp': Decimal(str(time.time())),
                'io_utilization_percentage': Decimal(
                    str(dev_metrics.io_utilization_percentage)
                ),
            }
        )


async def write_net(metrics: dict[str, NetMetrics]) -> None:
    db = await get_resource()
    table = await db.Table('net_metrics')
    for interface, intf_metrics in metrics.items():
        await table.put_item(
            Item={
                'metric': 'network',
                'intf_name': interface,
                'timestamp': Decimal(str(time.time())),
                'receive_bytes_per_sec': Decimal(
                    str(intf_metrics.receive_bytes_per_sec)
                ),
                'receive_packet_error_count': intf_metrics.receive_packet_error_count,
                'receive_packet_drop_count': intf_metrics.receive_packet_drop_count,
                'transmit_bytes_per_sec': Decimal(
                    str(intf_metrics.transmit_bytes_per_sec)
                ),
                'transmit_packet_error_count': intf_metrics.transmit_packet_error_count,
                'transmit_packet_drop_count': intf_metrics.transmit_packet_drop_count,
            }
        )


async def write_alert(alert: Alert) -> None:
    db = await get_resource()
    table = await db.Table('alerts')
    await table.put_item(
        Item={
            'pk': 'alert',
            'timestamp': Decimal(str(time.time())),
            'metric': alert.metric,
            'device': alert.device,
            'avg_short': Decimal(str(alert.avg_short)),
            'avg_long': Decimal(str(alert.avg_long)),
            'threshold': Decimal(str(alert.threshold)),
        }
    )


async def read_cpu_recent(limit: int) -> list:
    db = await get_resource()
    table = await db.Table('cpu_metrics')
    response = await table.query(
        KeyConditionExpression=Key('metric').eq('cpu'),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_ram_recent(limit: int) -> list:
    db = await get_resource()
    table = await db.Table('ram_metrics')
    response = await table.query(
        KeyConditionExpression=Key('metric').eq('ram'),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_disk_recent(device: str, limit: int) -> list:
    db = await get_resource()
    table = await db.Table('disk_metrics')
    response = await table.query(
        KeyConditionExpression=Key('dev_name').eq(device),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_net_recent(interface: str, limit: int) -> list:
    db = await get_resource()
    table = await db.Table('net_metrics')
    response = await table.query(
        KeyConditionExpression=Key('intf_name').eq(interface),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_alert(limit: int) -> list:
    db = await get_resource()
    table = await db.Table('alerts')
    response = await table.query(
        KeyConditionExpression=Key('pk').eq('alert'),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def get_known_devices() -> list:
    db = await get_resource()
    table = await db.Table('known_devices')
    response = await table.scan()
    return response['Items']


async def get_known_interfaces() -> list:
    db = await get_resource()
    table = await db.Table('known_interfaces')
    response = await table.scan()
    return response['Items']
