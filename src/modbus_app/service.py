from __future__ import annotations

from typing import Any

from pymodbus.client import ModbusSerialClient, ModbusTcpClient

from .models import (
    FunctionType,
    OperationResult,
    OperationSpec,
    RtuConnectionSettings,
    TcpConnectionSettings,
)


class ModbusService:
    def __init__(self) -> None:
        self._client: ModbusTcpClient | ModbusSerialClient | None = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def connect(self, settings: TcpConnectionSettings | RtuConnectionSettings) -> None:
        self.disconnect()
        if isinstance(settings, TcpConnectionSettings):
            client = ModbusTcpClient(
                settings.host,
                port=settings.port,
                timeout=settings.timeout,
                retries=settings.retries,
            )
        else:
            client = ModbusSerialClient(
                port=settings.port,
                baudrate=settings.baudrate,
                bytesize=settings.bytesize,
                parity=settings.parity,
                stopbits=settings.stopbits,
                timeout=settings.timeout,
                retries=settings.retries,
            )

        connected = bool(client.connect())
        if not connected:
            client.close()
            raise RuntimeError("Connection failed. Check host/port or serial settings.")

        self._client = client

    def disconnect(self) -> None:
        if self._client is None:
            return
        self._client.close()
        self._client = None

    def execute(self, operation: OperationSpec) -> OperationResult:
        client = self._require_client()
        response: Any
        function = operation.function
        if function == FunctionType.READ_COILS:
            response = client.read_coils(
                operation.address,
                count=operation.count,
                device_id=operation.device_id,
            )
            return self._build_bit_read_result(operation, response, "coil")
        if function == FunctionType.READ_DISCRETE_INPUTS:
            response = client.read_discrete_inputs(
                operation.address,
                count=operation.count,
                device_id=operation.device_id,
            )
            return self._build_bit_read_result(operation, response, "discrete input")
        if function == FunctionType.READ_HOLDING_REGISTERS:
            response = client.read_holding_registers(
                operation.address,
                count=operation.count,
                device_id=operation.device_id,
            )
            return self._build_register_read_result(operation, response, "holding register")
        if function == FunctionType.READ_INPUT_REGISTERS:
            response = client.read_input_registers(
                operation.address,
                count=operation.count,
                device_id=operation.device_id,
            )
            return self._build_register_read_result(operation, response, "input register")
        if function == FunctionType.WRITE_SINGLE_COIL:
            self._require_values(operation, expected=1)
            response = client.write_coil(
                operation.address,
                bool(operation.values[0]),
                device_id=operation.device_id,
            )
            return self._build_write_result(operation, response, "coil")
        if function == FunctionType.WRITE_MULTIPLE_COILS:
            self._require_values(operation, expected=operation.count)
            response = client.write_coils(
                operation.address,
                [bool(value) for value in operation.values],
                device_id=operation.device_id,
            )
            return self._build_write_result(operation, response, "coils")
        if function == FunctionType.WRITE_SINGLE_REGISTER:
            self._require_values(operation, expected=1)
            response = client.write_register(
                operation.address,
                int(operation.values[0]),
                device_id=operation.device_id,
            )
            return self._build_write_result(operation, response, "register")
        if function == FunctionType.WRITE_MULTIPLE_REGISTERS:
            self._require_values(operation, expected=operation.count)
            response = client.write_registers(
                operation.address,
                [int(value) for value in operation.values],
                device_id=operation.device_id,
            )
            return self._build_write_result(operation, response, "registers")

        raise RuntimeError(f"Unsupported function: {function}")

    def _require_client(self) -> ModbusTcpClient | ModbusSerialClient:
        if self._client is None:
            raise RuntimeError("Not connected to a Modbus device.")
        return self._client

    @staticmethod
    def _raise_for_error(response: Any) -> None:
        if response is None:
            raise RuntimeError("No response received from device.")
        if hasattr(response, "isError") and response.isError():
            raise RuntimeError(f"Modbus error: {response}")

    @staticmethod
    def _require_values(operation: OperationSpec, expected: int) -> None:
        if len(operation.values) != expected:
            raise RuntimeError(
                f"Expected {expected} value(s) for {operation.function.value}, "
                f"received {len(operation.values)}."
            )

    def _build_bit_read_result(
        self,
        operation: OperationSpec,
        response: Any,
        item_name: str,
    ) -> OperationResult:
        self._raise_for_error(response)
        values = [bool(value) for value in getattr(response, "bits", [])[: operation.count]]
        return OperationResult(
            function=operation.function,
            address=operation.address,
            count=len(values),
            values=values,
            summary=f"Read {len(values)} {item_name}(s) from address {operation.address}.",
            raw_response=repr(response),
        )

    def _build_register_read_result(
        self,
        operation: OperationSpec,
        response: Any,
        item_name: str,
    ) -> OperationResult:
        self._raise_for_error(response)
        values = [int(value) for value in getattr(response, "registers", [])[: operation.count]]
        return OperationResult(
            function=operation.function,
            address=operation.address,
            count=len(values),
            values=values,
            summary=f"Read {len(values)} {item_name}(s) from address {operation.address}.",
            raw_response=repr(response),
        )

    def _build_write_result(
        self,
        operation: OperationSpec,
        response: Any,
        item_name: str,
    ) -> OperationResult:
        self._raise_for_error(response)
        count = operation.count if operation.function.uses_multiple_values else 1
        return OperationResult(
            function=operation.function,
            address=operation.address,
            count=count,
            values=list(operation.values),
            summary=f"Wrote {count} {item_name}(s) starting at address {operation.address}.",
            raw_response=repr(response),
        )
