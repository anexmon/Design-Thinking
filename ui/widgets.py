
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QPainter


class Panel(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("surface")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(12)


class MetricPanel(Panel):

    def __init__(
        self,
        title,
        value="—",
        subtitle="",
        parent=None
    ):
        super().__init__(parent)

        self.layout.addWidget(
            QLabel(title.upper(), objectName="eyebrow")
        )

        self.value_label = QLabel(value)

        self.value_label.setStyleSheet(
            "font-size:28px;"
            "font-weight:700;"
            "color:#F0EBDD;"
        )

        self.layout.addWidget(self.value_label)

        self.sub_label = QLabel(
            subtitle,
            objectName="muted"
        )

        self.layout.addWidget(self.sub_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class PulseDot(QFrame):

    def __init__(self, color="#A2AA8A", parent=None):
        super().__init__(parent)

        self.color = QColor(color)
        self.phase = 0.0

        self.setFixedSize(14, 14)

        self.anim = QPropertyAnimation(
            self,
            b"phase",
            self
        )

        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(1500)
        self.anim.setLoopCount(-1)

        self.anim.setEasingCurve(
            QEasingCurve.InOutSine
        )

        self.anim.start()

    def get_phase(self):
        return self.phase

    def set_phase(self, value):
        self.phase = value
        self.update()

    phase_prop = Property(
        float,
        get_phase,
        set_phase
    )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)

        painter.drawEllipse(3, 3, 8, 8)

        alpha = int(40 * (1 - self.phase))

        painter.setBrush(
            QColor(
                self.color.red(),
                self.color.green(),
                self.color.blue(),
                alpha
            )
        )

        radius = 5 + int(5 * self.phase)

        painter.drawEllipse(
            7 - radius // 2,
            7 - radius // 2,
            radius,
            radius
        )
