CPU_TABLE = {
    'TableName': 'cpu_metrics',
    'KeySchema': [
        {
            'AttributeName': 'metric',
            'KeyType': 'HASH',
        },
        {
            'AttributeName': 'timestamp',
            'KeyType': 'RANGE',
        },
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'metric', 'AttributeType': 'S'},
        {'AttributeName': 'metric', 'AttributeType': 'N'},
    ],
    'BillingMode': 'PAY_PER_REQUEST',
}

RAM_TABLE = {
    'TableName': 'ram_metrics',
    'KeySchema': [
        {'AttributeName': 'metric', 'KeyType': 'HASH'},
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'},
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'metric', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'N'},
    ],
    'BillingMode': 'PAY_PER_REQUEST',
}

DISK_TABLE = {
    'TableName': 'disk_metrics',
    'KeySchema': [
        {'AttributeName': 'dev_name', 'KeyType': 'HASH'},
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'},
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'dev_name', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'N'},
    ],
    'BillingMode': 'PAY_PER_REQUEST',
}

NET_TABLE = {
    'TableName': 'net_metrics',
    'KeySchema': [
        {'AttributeName': 'intf_name', 'KeyType': 'HASH'},
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'},
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'intf_name', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'N'},
    ],
    'BillingMode': 'PAY_PER_REQUEST',
}

KNOWN_DEVICES_TABLE = {
    'TableName': 'known_devices',
    'KeySchema': [{'AttributeName': 'device', 'KeyType': 'HASH'}],
    'AttributeDefinitions': [{'AttributeName': 'device', 'AttributeType': 'S'}],
    'BillingMode': 'PAY_PER_REQUEST',
}

KNOWN_INTERFACES_TABLE = {
    'TableName': 'known_interfaces',
    'KeySchema': [{'AttributeName': 'interface', 'KeyType': 'HASH'}],
    'AttributeDefinitions': [{'AttributeName': 'interface', 'AttributeType': 'S'}],
    'BillingMode': 'PAY_PER_REQUEST',
}

ALERTS_TABLE = {
    'TableName': 'alerts',
    'KeySchema': [
        {'AttributeName': 'metric', 'KeyType': 'HASH'},
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'},
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'metric', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'N'},
    ],
    'BillingMode': 'PAY_PER_REQUEST',
}
