from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton
from .widgets import Panel

class StatusPanel(Panel):
    def __init__(self):
        super().__init__()
        self.state_label = QLabel("NORMAL")
        self.state_label.setStyleSheet("font-size:25px;font-weight:800;color:#63ddc7;")
        self.timer_label = QLabel("SYSTEM NOMINAL", objectName="muted")
        self.layout.addWidget(QLabel("MONITORING STATUS", objectName="eyebrow"))
        self.layout.addWidget(self.state_label)
        self.layout.addWidget(self.timer_label)
        self.cancel_button = QPushButton("Cancel verification")
        self.cancel_button.setObjectName("danger")
        self.cancel_button.hide()
        self.reset_button = QPushButton("Reset system")
        self.reset_button.hide()
        self.layout.addWidget(self.cancel_button)
        self.layout.addWidget(self.reset_button)
    def update_state(self, state, remaining=0):
        self.state_label.setText(state)
        colors = {"NORMAL":"#63ddc7","VERIFYING":"#ffbf69","CANCELLED":"#8ca4bb","ESCALATED":"#ff6474"}
        self.state_label.setStyleSheet(f"font-size:25px;font-weight:800;color:{colors.get(state,'#fff')};")
        if state == "VERIFYING":
            self.timer_label.setText(f"Please confirm your safety · {remaining:04.1f}s")
            self.cancel_button.show()
            self.reset_button.hide()
        elif state == "ESCALATED":
            self.timer_label.setText("DEMO ESCALATION STATE · NO SERVICES CONTACTED")
            self.cancel_button.hide()
            self.reset_button.show()
        elif state == "CANCELLED":
            self.timer_label.setText("Verification cancelled")
            self.cancel_button.hide()
            self.reset_button.show()
        else:
            self.timer_label.setText("System nominal · Hospital status: SIMULATED")
            self.cancel_button.hide()
            self.reset_button.hide()
