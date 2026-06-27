from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TransportType(StrEnum):
    TCP = "tcp"
    RTU = "rtu"


class FunctionType(StrEnum):
    READ_COILS = "read_coils"
    READ_DISCRETE_INPUTS = "read_discrete_inputs"
    READ_HOLDING_REGISTERS = "read_holding_registers"
    READ_INPUT_REGISTERS = "read_input_registers"
    WRITE_SINGLE_COIL = "write_single_coil"
    WRITE_MULTIPLE_COILS = "write_multiple_coils"
    WRITE_SINGLE_REGISTER = "write_single_register"
    WRITE_MULTIPLE_REGISTERS = "write_multiple_registers"

    @property
    def is_read(self) -> bool:
        return self in {
            FunctionType.READ_COILS,
            FunctionType.READ_DISCRETE_INPUTS,
            FunctionType.READ_HOLDING_REGISTERS,
            FunctionType.READ_INPUT_REGISTERS,
        }

    @property
    def is_write(self) -> bool:
        return not self.is_read

    @property
    def uses_bits(self) -> bool:
        return self in {
            FunctionType.READ_COILS,
            FunctionType.READ_DISCRETE_INPUTS,
            FunctionType.WRITE_SINGLE_COIL,
            FunctionType.WRITE_MULTIPLE_COILS,
        }

    @property
    def uses_multiple_values(self) -> bool:
        return self in {
            FunctionType.WRITE_MULTIPLE_COILS,
            FunctionType.WRITE_MULTIPLE_REGISTERS,
        }


@dataclass(slots=True)
class TcpConnectionSettings:
    host: str = "127.0.0.1"
    port: int = 502
    timeout: float = 3.0
    retries: int = 3

    transport: TransportType = field(default=TransportType.TCP, init=False)


@dataclass(slots=True)
class RtuConnectionSettings:
    port: str = "COM1"
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = "N"
    stopbits: int = 1
    timeout: float = 1.0
    retries: int = 3

    transport: TransportType = field(default=TransportType.RTU, init=False)


@dataclass(slots=True)
class OperationSpec:
    function: FunctionType
    address: int
    count: int = 1
    device_id: int = 1
    values: list[int | bool] = field(default_factory=list)


@dataclass(slots=True)
class OperationResult:
    function: FunctionType
    address: int
    count: int
    values: list[int | bool] = field(default_factory=list)
    summary: str = ""
    raw_response: str = ""
