
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox
)
from .widgets import Panel
from core.arduino_controller import ArduinoController


class SettingsPage(QWidget):
    def __init__(self, arduino):
        super().__init__()
        self.arduino = arduino

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)

        title = QLabel("Hardware & settings")
        title.setStyleSheet("font-size:27px;font-weight:750;")
        layout.addWidget(title)

        panel = Panel()
        panel.layout.addWidget(
            QLabel("ESP32 LED CONTROLLER", objectName="eyebrow")
        )

        row = QHBoxLayout()

        self.port = QComboBox()
        self.refresh_ports()
        row.addWidget(self.port, 1)

        refresh = QPushButton("Refresh ports")
        refresh.clicked.connect(self.refresh_ports)
        row.addWidget(refresh)

        connect = QPushButton("Connect")
        connect.setObjectName("primary")
        connect.clicked.connect(self.connect_arduino)
        row.addWidget(connect)

        disconnect = QPushButton("Disconnect")
        disconnect.clicked.connect(self.disconnect_arduino)
        row.addWidget(disconnect)

        panel.layout.addLayout(row)

        self.status = QLabel("ESP32 not connected")
        self.status.setObjectName("muted")
        panel.layout.addWidget(self.status)

        panel.layout.addWidget(
            QLabel(
                "LED wiring: Red D22 · Green D23 · "
                "220Ω resistors · Common GND",
                objectName="muted"
            )
        )

        layout.addWidget(panel)

        note = QLabel(
            "Detection sensitivity is configured in config.py. "
            "Changes should be tested carefully. The movement detector "
            "is experimental and is not a medical device."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)

        layout.addStretch()

    def refresh_ports(self):
        self.port.clear()
        self.port.addItems(ArduinoController.available_ports())

    def connect_arduino(self):
        selected = self.port.currentText()

        if not selected:
            QMessageBox.warning(
                self, "No port", "No serial port selected."
            )
            return

        try:
            self.arduino.connect(selected, baud=9600)
            self.status.setText(f"Connected to ESP32 on {selected}")
        except Exception as exc:
            self.status.setText(f"Connection failed: {exc}")

    def disconnect_arduino(self):
        self.arduino.disconnect()
        self.status.setText("ESP32 disconnected")
