from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

from .models import OperationSpec, RtuConnectionSettings, TcpConnectionSettings
from .service import ModbusService


class ModbusWorker(QObject):
    connection_changed = Signal(bool, str)
    operation_completed = Signal(object)
    operation_failed = Signal(str)
    log_message = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._service = ModbusService()

    @Slot(object)
    def connect_transport(self, settings: TcpConnectionSettings | RtuConnectionSettings) -> None:
        try:
            self._service.connect(settings)
        except Exception as exc:
            self.log_message.emit(self._stamp(f"Connect failed: {exc}"))
            self.connection_changed.emit(False, "Disconnected")
            self.operation_failed.emit(str(exc))
            return

        transport_name = settings.transport.value.upper()
        target = getattr(settings, "host", getattr(settings, "port", ""))
        self.log_message.emit(self._stamp(f"Connected via {transport_name} to {target}."))
        self.connection_changed.emit(True, f"Connected ({transport_name})")

    @Slot()
    def disconnect_transport(self) -> None:
        self._service.disconnect()
        self.log_message.emit(self._stamp("Disconnected from device."))
        self.connection_changed.emit(False, "Disconnected")

    @Slot(object)
    def execute_operation(self, operation: OperationSpec) -> None:
        try:
            result = self._service.execute(operation)
        except Exception as exc:
            self.log_message.emit(self._stamp(f"Operation failed: {exc}"))
            self.operation_failed.emit(str(exc))
            return

        self.log_message.emit(self._stamp(result.summary))
        self.operation_completed.emit(result)

    @staticmethod
    def _stamp(message: str) -> str:
        return f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
