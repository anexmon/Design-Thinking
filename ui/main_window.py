
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame
)
from PySide6.QtCore import QTimer

from core.monitoring_worker import MonitoringWorker
from core.emergency_manager import EmergencyManager
from core.event_logger import EventLogger
from core.arduino_controller import ArduinoController

from config import VERIFY_SECONDS, INFERENCE_INTERVAL, DB_PATH

from .dashboard import Dashboard
from .event_history import EventHistory
from .settings_page import SettingsPage
from .widgets import PulseDot


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sentinel · Monitoring")
        self.resize(1480, 900)
        self.setMinimumSize(1100, 720)

        self.logger = EventLogger(DB_PATH)
        self.emergency = EmergencyManager(VERIFY_SECONDS)
        self.arduino = ArduinoController()

        self.worker = None
        self.last_detection = {}

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        main = QHBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # SIDEBAR
        sidebar = QFrame()
        sidebar.setFixedWidth(225)
        sidebar.setStyleSheet(
            "background:#20231D;"
            "border-right:1px solid #393D32;"
        )

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 24, 18, 18)

        brand = QLabel("◈  SENTINEL")
        brand.setStyleSheet(
            "font-size:19px;"
            "font-weight:850;"
            "letter-spacing:2px;"
            "color:#D8D1BD;"
        )

        side.addWidget(brand)
        side.addWidget(
            QLabel("MONITORING SYSTEM", objectName="eyebrow")
        )
        side.addSpacing(30)

        # NAVIGATION
        self.stack = QStackedWidget()

        self.dashboard = Dashboard()
        self.history = EventHistory(self.logger)
        self.settings = SettingsPage(self.arduino)

        self.pages = [
            self.dashboard,
            self.history,
            self.settings
        ]

        self.nav_buttons = []

        labels = [
            "Overview / Live",
            "Event history",
            "Hardware & settings"
        ]

        for i, label in enumerate(labels):
            button = QPushButton(label)
            button.setObjectName("nav")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, index=i:
                self.navigate(index)
            )

            side.addWidget(button)
            self.nav_buttons.append(button)

        self.nav_buttons[0].setChecked(True)

        side.addStretch()

        side.addWidget(
            QLabel("PROTOTYPE BUILD · 01", objectName="muted")
        )

        main.addWidget(sidebar)

        # MAIN CONTENT
        content = QVBoxLayout()

        top = QHBoxLayout()
        top.setContentsMargins(28, 15, 28, 12)

        top.addWidget(PulseDot())
        top.addWidget(QLabel("LOCAL MONITORING SESSION"))
        top.addStretch()

        top.addWidget(
            QLabel(
                "HOSPITAL LINK: SIMULATED",
                objectName="eyebrow"
            )
        )

        content.addLayout(top)

        for page in self.pages:
            self.stack.addWidget(page)

        content.addWidget(self.stack, 1)
        main.addLayout(content, 1)

        # BUTTON CONNECTIONS
        self.dashboard.start_button.clicked.connect(
            self.start_monitoring
        )

        self.dashboard.stop_button.clicked.connect(
            self.stop_monitoring
        )

        self.dashboard.status.cancel_button.clicked.connect(
            self.cancel_verification
        )

        self.dashboard.status.reset_button.clicked.connect(
            self.reset_system
        )

        # STATUS TIMER
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(100)

        self.navigate(0)

    def navigate(self, index):

        self.stack.setCurrentIndex(index)

        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

        if index == 1:
            self.history.refresh()

    def start_monitoring(self):

        if self.worker and self.worker.isRunning():
            return

        self.worker = MonitoringWorker(
            0,
            INFERENCE_INTERVAL,
            self
        )

        self.worker.frame_ready.connect(
            self.dashboard.camera.set_frame
        )

        self.worker.status_ready.connect(
            self.on_camera_status
        )

        self.worker.fps_ready.connect(
            lambda fps:
            self.dashboard.fps.set_value(f"{fps:.0f}")
        )

        self.worker.detection_ready.connect(
            self.on_detection
        )

        self.dashboard.camera.set_status(
            "STARTING CAMERA"
        )

        self.worker.start()

        self.logger.log(
            "MONITORING_STARTED",
            self.emergency.state,
            self.emergency.state,
            "Camera worker started"
        )

    def stop_monitoring(self):

        if self.worker and self.worker.isRunning():
            self.worker.stop()

        self.dashboard.camera.set_status(
            "MONITORING STOPPED"
        )

        self.logger.log(
            "MONITORING_STOPPED",
            self.emergency.state,
            self.emergency.state,
            "User stopped monitoring"
        )

    def on_camera_status(self, text):

        self.dashboard.camera_status.setText(
            "Camera: " + text
        )

        self.dashboard.camera.set_status(text)

        self.dashboard.pose.set_value(
            "ONLINE"
            if "ONLINE" in text
            else "OFFLINE"
        )

    def on_detection(self, result):

        self.last_detection = result

        self.dashboard.movement.set_value(
            result.get("label", "—")
        )

        transition = self.emergency.update_detection(
            bool(result.get("unusual"))
        )

        if transition:
            self.handle_transition(transition)

    def handle_transition(self, transition):

        old, new = transition

        self.logger.log(
            "STATE_CHANGE",
            old,
            new,
            "Movement anomaly verification workflow"
        )

        self.arduino.send_state(new)

        self.dashboard.status.update_state(
            new,
            self.emergency.remaining()
        )

    def cancel_verification(self):

        transition = self.emergency.cancel()

        if transition:
            self.handle_transition(transition)

    def reset_system(self):

        transition = self.emergency.reset()

        self.handle_transition(transition)

    def refresh_status(self):

        transition = self.emergency.tick()

        if transition:
            self.handle_transition(transition)

        self.dashboard.status.update_state(
            self.emergency.state,
            self.emergency.remaining()
        )

        self.dashboard.arduino_status.setText(
            "Arduino: "
            + (
                "connected"
                if self.arduino.connected
                else "not connected"
            )
        )

    def closeEvent(self, event):

        self.timer.stop()

        if self.worker and self.worker.isRunning():
            self.worker.stop()

        self.arduino.disconnect()

        event.accept()
