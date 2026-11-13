
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor


class CameraView(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(520, 330)

        self.image = None
        self.placeholder = "WAITING FOR CAMERA"

    def set_frame(self, image):

        self.image = image
        self.update()

    def set_status(self, text):

        self.placeholder = text
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.fillRect(
            self.rect(),
            QColor("#11130F")
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        if self.image:

            pixmap = QPixmap.fromImage(self.image)

            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            x = (
                self.width() - scaled.width()
            ) // 2

            y = (
                self.height() - scaled.height()
            ) // 2

            painter.drawPixmap(x, y, scaled)

        else:

            painter.setPen(
                QColor("#A6A493")
            )

            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                self.placeholder
                + "\n\nConnect a webcam to begin"
            )
