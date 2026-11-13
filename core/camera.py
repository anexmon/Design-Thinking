import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
import time

class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    camera_status = Signal(str)
    fps_ready = Signal(float)

    def __init__(self, camera_index=0, width=1280, height=720, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self._running = True

    def stop(self):
        self._running = False
        self.wait(2500)

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.camera_status.emit("CAMERA UNAVAILABLE")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera_status.emit("CAMERA ONLINE")
        previous = time.monotonic()
        frames = 0
        while self._running:
            ok, frame = cap.read()
            if not ok:
                self.camera_status.emit("CAMERA INTERRUPTED")
                time.sleep(0.1)
                continue
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch*w, QImage.Format_RGB888).copy()
            self.frame_ready.emit(qimg)
            frames += 1
            now = time.monotonic()
            if now - previous >= 1:
                self.fps_ready.emit(frames / (now - previous))
                frames = 0
                previous = now
        cap.release()
        self.camera_status.emit("CAMERA STOPPED")
