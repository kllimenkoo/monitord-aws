from contextlib import asynccontextmanager

from fastapi import FastAPI
from mangum import Mangum
from schemas import CpuResponse, DiskResponse, NetResponse, RamResponse
from storage import (
    get_known_devices,
    get_known_interfaces,
    read_alert,
    read_cpu,
    read_disk,
    read_net,
    read_ram,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get('/get_device_names')
async def get_device_names() -> list[str]:
    result = await get_known_devices()
    return [item['device'] for item in result]


@app.get('/get_interface_names')
async def get_interface_names() -> list[str]:
    result = await get_known_interfaces()
    return [item['interface'] for item in result]


@app.get('/alerts')
async def get_alerts(limit: int = 60):
    result = await read_alert(limit=limit)
    return {'alerts': result}


@app.get('/cpu', response_model=list[CpuResponse])
async def get_cpu(limit: int = 150) -> list[CpuResponse]:
    rows = await read_cpu(limit=limit)
    result = [
        CpuResponse(
            timestamp=row['timestamp'], usage_percentage=row['usage_percentage']
        )
        for row in rows
    ]
    return result


@app.get('/ram', response_model=list[RamResponse])
async def get_ram(limit: int = 150) -> list[RamResponse]:
    rows = await read_ram(limit=limit)
    result = [
        RamResponse(
            timestamp=row['timestamp'],
            mem_usage_percentage=row['mem_usage_percentage'],
            swap_usage_percentage=row['swap_usage_percentage'],
        )
        for row in rows
    ]
    return result


@app.get('/disk/{device}', response_model=list[DiskResponse])
async def get_disk(device: str, limit: int = 150) -> list[DiskResponse]:
    rows = await read_disk(device=device, limit=limit)
    result = [
        DiskResponse(
            timestamp=row['timestamp'],
            device=row['dev_name'],
            io_utilization_percentage=row['io_utilization_percentage'],
        )
        for row in rows
    ]
    return result


@app.get('/net/{interface}', response_model=list[NetResponse])
async def get_interface(interface: str, limit: int = 150) -> list[NetResponse]:
    rows = await read_net(interface=interface, limit=limit)
    result = [
        NetResponse(
            timestamp=row['timestamp'],
            interface=row['intf_name'],
            receive_bytes_per_sec=row['receive_bytes_per_sec'],
            transmit_bytes_per_sec=row['transmit_bytes_per_sec'],
        )
        for row in rows
    ]
    return result


handler = Mangum(app)
