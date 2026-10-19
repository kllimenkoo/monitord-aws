import os

import aioboto3
from boto3.dynamodb.conditions import Key

_resource = None


async def get_resource():
    global _resource
    if _resource is None:
        session = aioboto3.Session()
        _resource = await session.resource(
            'dynamodb', region_name=os.environ['AWS_REGION']
        ).__aenter__()
    return _resource


async def read_cpu(limit: int) -> list:
    db = await get_resource()
    table = await db.Table('cpu_metrics')
    response = await table.query(
        KeyConditionExpression=Key('metric').eq('cpu'),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_ram(limit: int) -> list:
    db = await get_resource()
    table = await db.Table('ram_metrics')
    response = await table.query(
        KeyConditionExpression=Key('metric').eq('ram'),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_disk(device: str, limit: int) -> list:
    db = await get_resource()
    table = await db.Table('disk_metrics')
    response = await table.query(
        KeyConditionExpression=Key('dev_name').eq(device),
        ScanIndexForward=False,
        Limit=limit,
    )
    return response['Items']


async def read_net(interface: str, limit: int) -> list:
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
