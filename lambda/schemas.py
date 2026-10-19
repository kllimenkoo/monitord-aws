from pydantic import BaseModel


class CpuResponse(BaseModel):
    timestamp: float
    usage_percentage: float


class RamResponse(BaseModel):
    timestamp: float
    mem_usage_percentage: float
    swap_usage_percentage: float


class DiskResponse(BaseModel):
    timestamp: float
    device: str
    io_utilization_percentage: float


class NetResponse(BaseModel):
    timestamp: float
    interface: str
    receive_bytes_per_sec: float
    transmit_bytes_per_sec: float
