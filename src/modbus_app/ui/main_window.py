from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import QThread, QTimer, Qt, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..branding import CAPABILITY_LABEL, TAGLINE, WINDOW_TITLE, create_app_icon, create_brand_pixmap
from ..models import (
    FunctionType,
    OperationResult,
    OperationSpec,
    RtuConnectionSettings,
    TcpConnectionSettings,
    TransportType,
)
from ..worker import ModbusWorker


FUNCTION_LABELS: list[tuple[str, FunctionType]] = [
    ("Read Coils", FunctionType.READ_COILS),
    ("Read Discrete Inputs", FunctionType.READ_DISCRETE_INPUTS),
    ("Read Holding Registers", FunctionType.READ_HOLDING_REGISTERS),
    ("Read Input Registers", FunctionType.READ_INPUT_REGISTERS),
    ("Write Single Coil", FunctionType.WRITE_SINGLE_COIL),
    ("Write Multiple Coils", FunctionType.WRITE_MULTIPLE_COILS),
    ("Write Single Register", FunctionType.WRITE_SINGLE_REGISTER),
    ("Write Multiple Registers", FunctionType.WRITE_MULTIPLE_REGISTERS),
]


class MainWindow(QMainWindow):
    connect_requested = Signal(object)
    disconnect_requested = Signal()
    execute_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(create_app_icon())
        self.resize(1100, 760)
        self.setMinimumSize(860, 620)

        self._thread = QThread(self)
        self._worker = ModbusWorker()
        self._worker.moveToThread(self._thread)
        self._thread.start()

        self.connect_requested.connect(self._worker.connect_transport)
        self.disconnect_requested.connect(self._worker.disconnect_transport)
        self.execute_requested.connect(self._worker.execute_operation)
        self._worker.connection_changed.connect(self._on_connection_changed)
        self._worker.operation_completed.connect(self._on_operation_completed)
        self._worker.operation_failed.connect(self._on_operation_failed)
        self._worker.log_message.connect(self._append_log)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._trigger_poll)

        self._build_ui()
        self._on_transport_changed(0)
        self._on_function_changed(0)

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(14)
        root.setContentsMargins(14, 14, 14, 14)

        root.addWidget(self._build_brand_header())

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.setChildrenCollapsible(False)
        top_splitter.setHandleWidth(8)
        top_splitter.addWidget(self._wrap_scrollable_panel(self._build_connection_group()))
        top_splitter.addWidget(self._wrap_scrollable_panel(self._build_operation_group()))
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 4)
        top_splitter.setSizes([330, 500])

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(8)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self._build_diagnostics_group())
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 2)
        root.addWidget(main_splitter, 1)
        main_splitter.setSizes([360, 220])

    def _build_brand_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("brandHeader")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        mark = QLabel()
        mark.setPixmap(create_brand_pixmap(64))
        mark.setFixedSize(64, 64)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mark)

        copy_layout = QVBoxLayout()
        title = QLabel(WINDOW_TITLE)
        title.setObjectName("brandTitle")
        title.setWordWrap(True)
        subtitle = QLabel(TAGLINE)
        subtitle.setObjectName("brandSubtitle")
        subtitle.setWordWrap(True)
        copy_layout.addWidget(title)
        copy_layout.addWidget(subtitle)

        pill_row = QHBoxLayout()
        pill_row.setSpacing(10)
        for text in ("Creative Factory", CAPABILITY_LABEL):
            pill = self._create_wrapped_pill(text)
            pill_row.addWidget(pill)
        pill_row.addStretch(1)
        copy_layout.addLayout(pill_row)

        layout.addLayout(copy_layout, 1)
        return frame

    @staticmethod
    def _create_wrapped_pill(text: str) -> QLabel:
        pill = QLabel(text)
        pill.setObjectName("brandPill")
        pill.setWordWrap(True)
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        return pill

    @staticmethod
    def _wrap_scrollable_panel(widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(widget)
        return scroll

    def _build_connection_group(self) -> QGroupBox:
        group = QGroupBox("Device Connection")
        layout = QVBoxLayout(group)

        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.transport_combo = QComboBox()
        self.transport_combo.addItem("Modbus TCP", TransportType.TCP)
        self.transport_combo.addItem("Modbus RTU", TransportType.RTU)
        self.transport_combo.currentIndexChanged.connect(self._on_transport_changed)
        form.addRow("Transport", self.transport_combo)

        self.transport_stack = QStackedWidget()
        self.transport_stack.addWidget(self._build_tcp_page())
        self.transport_stack.addWidget(self._build_rtu_page())
        form.addRow(self.transport_stack)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._request_connect)
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_requested.emit)
        self.disconnect_button.setEnabled(False)
        buttons.addWidget(self.connect_button)
        buttons.addWidget(self.disconnect_button)
        layout.addLayout(buttons)

        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("statusPill")
        self.status_label.setProperty("connected", False)
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.status_label)
        layout.addStretch(1)
        return group

    def _build_tcp_page(self) -> QWidget:
        page = QWidget()
        layout = QFormLayout(page)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.tcp_host_edit = QLineEdit("127.0.0.1")
        self.tcp_port_spin = QSpinBox()
        self.tcp_port_spin.setRange(1, 65535)
        self.tcp_port_spin.setValue(502)
        self.tcp_timeout_spin = QDoubleSpinBox()
        self.tcp_timeout_spin.setRange(0.1, 60.0)
        self.tcp_timeout_spin.setValue(3.0)
        self.tcp_timeout_spin.setSingleStep(0.5)
        self.tcp_retries_spin = QSpinBox()
        self.tcp_retries_spin.setRange(0, 10)
        self.tcp_retries_spin.setValue(3)

        layout.addRow("Host", self.tcp_host_edit)
        layout.addRow("Port", self.tcp_port_spin)
        layout.addRow("Timeout (s)", self.tcp_timeout_spin)
        layout.addRow("Retries", self.tcp_retries_spin)
        return page

    def _build_rtu_page(self) -> QWidget:
        page = QWidget()
        layout = QFormLayout(page)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.rtu_port_edit = QLineEdit("COM1")
        self.rtu_baud_spin = QSpinBox()
        self.rtu_baud_spin.setRange(110, 921600)
        self.rtu_baud_spin.setValue(9600)
        self.rtu_bytesize_spin = QSpinBox()
        self.rtu_bytesize_spin.setRange(5, 8)
        self.rtu_bytesize_spin.setValue(8)
        self.rtu_parity_combo = QComboBox()
        self.rtu_parity_combo.addItems(["N", "E", "O"])
        self.rtu_stopbits_combo = QComboBox()
        self.rtu_stopbits_combo.addItem("1", 1)
        self.rtu_stopbits_combo.addItem("2", 2)
        self.rtu_timeout_spin = QDoubleSpinBox()
        self.rtu_timeout_spin.setRange(0.1, 60.0)
        self.rtu_timeout_spin.setValue(1.0)
        self.rtu_timeout_spin.setSingleStep(0.5)
        self.rtu_retries_spin = QSpinBox()
        self.rtu_retries_spin.setRange(0, 10)
        self.rtu_retries_spin.setValue(3)

        layout.addRow("COM Port", self.rtu_port_edit)
        layout.addRow("Baudrate", self.rtu_baud_spin)
        layout.addRow("Bytesize", self.rtu_bytesize_spin)
        layout.addRow("Parity", self.rtu_parity_combo)
        layout.addRow("Stop Bits", self.rtu_stopbits_combo)
        layout.addRow("Timeout (s)", self.rtu_timeout_spin)
        layout.addRow("Retries", self.rtu_retries_spin)
        return page

    def _build_operation_group(self) -> QGroupBox:
        group = QGroupBox("Command Center")
        layout = QVBoxLayout(group)

        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.function_combo = QComboBox()
        for label, function in FUNCTION_LABELS:
            self.function_combo.addItem(label, function)
        self.function_combo.currentIndexChanged.connect(self._on_function_changed)

        self.device_id_spin = QSpinBox()
        self.device_id_spin.setRange(0, 255)
        self.device_id_spin.setValue(1)
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 65535)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 125)
        self.count_spin.setValue(10)
        self.values_edit = QLineEdit()
        self.values_hint = QLabel()
        self.values_hint.setWordWrap(True)
        self.values_hint.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        form.addRow("Function", self.function_combo)
        form.addRow("Unit ID", self.device_id_spin)
        form.addRow("Address", self.address_spin)
        form.addRow("Count", self.count_spin)
        form.addRow("Values", self.values_edit)
        layout.addLayout(form)
        layout.addWidget(self.values_hint)

        action_row = QHBoxLayout()
        self.execute_button = QPushButton("Read")
        self.execute_button.clicked.connect(self._execute_once)
        self.poll_checkbox = QCheckBox("Poll")
        self.poll_checkbox.toggled.connect(self._toggle_polling)
        self.poll_interval_spin = QSpinBox()
        self.poll_interval_spin.setRange(100, 60000)
        self.poll_interval_spin.setValue(1000)
        self.poll_interval_spin.setSuffix(" ms")
        action_row.addWidget(self.execute_button)
        action_row.addWidget(self.poll_checkbox)
        action_row.addWidget(self.poll_interval_spin)
        action_row.addStretch(1)
        layout.addLayout(action_row)
        layout.addStretch(1)
        return group

    def _build_results_group(self) -> QGroupBox:
        group = QGroupBox("Values")
        layout = QVBoxLayout(group)

        self.results_table = QTableWidget(0, 2)
        self.results_table.setHorizontalHeaderLabels(["Address", "Value"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.summary_label = QLabel("No operation executed.")
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.results_table, 1)
        layout.addWidget(self.summary_label)
        return group

    def _build_raw_response_group(self) -> QGroupBox:
        group = QGroupBox("Raw Response")
        layout = QVBoxLayout(group)
        self.raw_response_view = QPlainTextEdit()
        self.raw_response_view.setReadOnly(True)
        self.raw_response_view.setPlaceholderText("Raw Modbus response will appear here.")
        self.raw_response_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.raw_response_view)
        return group

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Activity Log")
        layout = QVBoxLayout(group)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.log_view)
        return group

    def _build_diagnostics_group(self) -> QGroupBox:
        group = QGroupBox("Diagnostics")
        layout = QVBoxLayout(group)

        tabs = QTabWidget()
        tabs.addTab(self._build_results_group(), "Values")
        tabs.addTab(self._build_raw_response_group(), "Raw Response")
        tabs.addTab(self._build_log_group(), "Activity Log")
        layout.addWidget(tabs)
        return group

    def _request_connect(self) -> None:
        settings = self._current_connection_settings()
        self.connect_button.setEnabled(False)
        self.connect_requested.emit(settings)

    def _current_connection_settings(self) -> TcpConnectionSettings | RtuConnectionSettings:
        transport = TransportType(self.transport_combo.currentData())
        if transport == TransportType.TCP:
            return TcpConnectionSettings(
                host=self.tcp_host_edit.text().strip() or "127.0.0.1",
                port=self.tcp_port_spin.value(),
                timeout=self.tcp_timeout_spin.value(),
                retries=self.tcp_retries_spin.value(),
            )
        return RtuConnectionSettings(
            port=self.rtu_port_edit.text().strip() or "COM1",
            baudrate=self.rtu_baud_spin.value(),
            bytesize=self.rtu_bytesize_spin.value(),
            parity=self.rtu_parity_combo.currentText(),
            stopbits=int(self.rtu_stopbits_combo.currentData()),
            timeout=self.rtu_timeout_spin.value(),
            retries=self.rtu_retries_spin.value(),
        )

    def _current_operation(self) -> OperationSpec:
        function = FunctionType(self.function_combo.currentData())
        count = self.count_spin.value()
        values = self._parse_values(function, self.values_edit.text(), count)
        if function in {
            FunctionType.WRITE_SINGLE_COIL,
            FunctionType.WRITE_SINGLE_REGISTER,
        }:
            count = 1
        return OperationSpec(
            function=function,
            address=self.address_spin.value(),
            count=count,
            device_id=self.device_id_spin.value(),
            values=values,
        )

    def _parse_values(
        self,
        function: FunctionType,
        text: str,
        count: int,
    ) -> list[int | bool]:
        if function.is_read:
            return []

        parts = [part.strip() for part in text.split(",") if part.strip()]
        if not parts:
            raise ValueError("Enter one or more values before writing.")

        if function.uses_bits:
            values = [self._parse_bool(part) for part in parts]
        else:
            values = [int(part, 0) for part in parts]

        if function.uses_multiple_values and len(values) != count:
            raise ValueError(f"Expected {count} values, received {len(values)}.")
        if not function.uses_multiple_values and len(values) != 1:
            raise ValueError("Single write operations need exactly one value.")
        return values

    @staticmethod
    def _parse_bool(raw: str) -> bool:
        normalized = raw.strip().lower()
        truthy = {"1", "true", "on", "yes"}
        falsy = {"0", "false", "off", "no"}
        if normalized in truthy:
            return True
        if normalized in falsy:
            return False
        raise ValueError(f"Invalid coil value: {raw}")

    def _execute_once(self) -> None:
        try:
            operation = self._current_operation()
        except ValueError as exc:
            self._show_error(str(exc))
            return

        if self.poll_checkbox.isChecked() and operation.function.is_write:
            self.poll_checkbox.setChecked(False)
        self.execute_requested.emit(operation)

    def _toggle_polling(self, enabled: bool) -> None:
        function = FunctionType(self.function_combo.currentData())
        if enabled and function.is_write:
            self.poll_checkbox.setChecked(False)
            self._show_error("Polling is available for read functions only.")
            return

        if enabled:
            self._poll_timer.start(self.poll_interval_spin.value())
            self._append_log("Polling enabled.")
            self._trigger_poll()
            return

        self._poll_timer.stop()
        self._append_log("Polling disabled.")

    def _trigger_poll(self) -> None:
        try:
            operation = self._current_operation()
        except ValueError as exc:
            self.poll_checkbox.setChecked(False)
            self._show_error(str(exc))
            return

        if operation.function.is_write:
            self.poll_checkbox.setChecked(False)
            return
        self.execute_requested.emit(operation)

    def _on_transport_changed(self, index: int) -> None:
        self.transport_stack.setCurrentIndex(index)

    def _on_function_changed(self, index: int) -> None:
        function_data = self.function_combo.itemData(index)
        function = FunctionType(function_data) if function_data is not None else None
        if function is None:
            return

        is_read = function.is_read
        self.execute_button.setText("Read" if is_read else "Write")
        self.values_edit.setEnabled(not is_read)

        if function in {
            FunctionType.WRITE_SINGLE_COIL,
            FunctionType.WRITE_SINGLE_REGISTER,
        }:
            self.count_spin.setValue(1)
            self.count_spin.setEnabled(False)
        else:
            self.count_spin.setEnabled(True)

        if is_read:
            self.count_spin.setRange(1, 2000 if function.uses_bits else 125)
            self.values_edit.clear()
            self.values_edit.setPlaceholderText("")
            self.values_hint.setText("Read functions ignore the values field.")
        elif function.uses_bits and function.uses_multiple_values:
            self.count_spin.setRange(1, 1968)
            self.values_edit.setPlaceholderText("1,0,1,1")
            self.values_hint.setText("Enter comma-separated coil values. Accepted: 1/0, true/false, on/off.")
        elif function.uses_bits:
            self.values_edit.setPlaceholderText("1")
            self.values_hint.setText("Enter a single coil value: 1/0, true/false, on/off.")
        elif function.uses_multiple_values:
            self.count_spin.setRange(1, 123)
            self.values_edit.setPlaceholderText("100,200,300")
            self.values_hint.setText("Enter comma-separated register values. Decimal and 0x-prefixed hex are supported.")
        else:
            self.values_edit.setPlaceholderText("123")
            self.values_hint.setText("Enter one register value. Decimal and 0x-prefixed hex are supported.")

        if is_read and self.poll_checkbox.isChecked():
            self._poll_timer.start(self.poll_interval_spin.value())
        elif not is_read and self.poll_checkbox.isChecked():
            self.poll_checkbox.setChecked(False)

    def _on_connection_changed(self, connected: bool, status_text: str) -> None:
        self.status_label.setText(status_text)
        self.status_label.setProperty("connected", connected)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)

    def _on_operation_completed(self, result: OperationResult) -> None:
        self.summary_label.setText(result.summary)
        self.raw_response_view.setPlainText(result.raw_response)
        self._populate_table(result)

    def _populate_table(self, result: OperationResult) -> None:
        values = list(result.values)
        self.results_table.setRowCount(len(values))
        for row, (address, value) in enumerate(self._iter_rows(result.address, values)):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(address)))
            display_value = "ON" if value is True else "OFF" if value is False else str(value)
            self.results_table.setItem(row, 1, QTableWidgetItem(display_value))

        if not values:
            self.results_table.setRowCount(0)

    @staticmethod
    def _iter_rows(start_address: int, values: Iterable[int | bool]) -> Iterable[tuple[int, int | bool]]:
        for offset, value in enumerate(values):
            yield start_address + offset, value

    def _on_operation_failed(self, message: str) -> None:
        self._show_error(message)

    def _append_log(self, message: str) -> None:
        self.log_view.appendPlainText(message)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Modbus Error", message)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._poll_timer.stop()
        self.disconnect_requested.emit()
        self._thread.quit()
        self._thread.wait(3000)
        super().closeEvent(event)
