
import threading
import time
import cv2

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from .pose_detector import PoseDetector
from .movement_detector import MovementDetector


class FrameBuffer:
    """Stores only the newest camera frame and skeleton points."""

    def __init__(self):
        self.lock = threading.Lock()
        self.frame = None
        self.sequence = 0
        self.points = None

    def publish(self, frame):
        with self.lock:
            self.frame = frame
            self.sequence += 1

    def read(self):
        with self.lock:
            if self.frame is None:
                return None, self.sequence
            return self.frame.copy(), self.sequence

    def set_points(self, points):
        with self.lock:
            self.points = list(points) if points is not None else None

    def get_points(self):
        with self.lock:
            return list(self.points) if self.points is not None else None


CONNECTIONS = [
    (11, 12), (11, 13), (13, 15),
    (12, 14), (14, 16), (11, 23),
    (12, 24), (23, 24), (23, 25),
    (25, 27), (24, 26), (26, 28),
    (27, 29), (29, 31), (28, 30),
    (30, 32), (0, 1), (1, 2), (2, 3),
    (3, 7), (0, 4), (4, 5), (5, 6), (6, 8)
]


class CaptureThread(QThread):

    frame_ready = Signal(QImage)
    status_ready = Signal(str)
    fps_ready = Signal(float)

    def __init__(self, buffer, camera_index=0):
        super().__init__()
        self.buffer = buffer
        self.camera_index = camera_index
        self.running = True

    def stop(self):
        self.running = False
        if self.isRunning():
            self.wait(4000)

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            self.status_ready.emit("CAMERA UNAVAILABLE")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.status_ready.emit("CAMERA ONLINE")

        emitted_frames = 0
        fps_start = time.monotonic()
        last_display = 0.0

        # Limit GUI updates to approximately 24 FPS.
        display_interval = 1.0 / 24.0

        try:
            while self.running:
                success, frame = cap.read()

                if not success:
                    time.sleep(0.01)
                    continue

                frame = cv2.flip(frame, 1)

                # Always publish the newest frame for pose inference.
                self.buffer.publish(frame)

                now = time.monotonic()

                # Do not flood the GUI with frame signals.
                if now - last_display < display_interval:
                    continue

                last_display = now

                points = self.buffer.get_points()

                if points:
                    height, width = frame.shape[:2]

                    for a, b in CONNECTIONS:
                        if (
                            a < len(points)
                            and b < len(points)
                            and points[a] is not None
                            and points[b] is not None
                        ):
                            cv2.line(
                                frame,
                                (
                                    int(points[a][0] * width),
                                    int(points[a][1] * height)
                                ),
                                (
                                    int(points[b][0] * width),
                                    int(points[b][1] * height)
                                ),
                                (135, 155, 125),
                                2,
                                cv2.LINE_AA
                            )

                    for point in points:
                        if point is not None:
                            cv2.circle(
                                frame,
                                (
                                    int(point[0] * width),
                                    int(point[1] * height)
                                ),
                                3,
                                (215, 205, 180),
                                -1,
                                cv2.LINE_AA
                            )

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = rgb.shape

                image = QImage(
                    rgb.data,
                    width,
                    height,
                    channels * width,
                    QImage.Format_RGB888
                ).copy()

                self.frame_ready.emit(image)

                emitted_frames += 1
                now = time.monotonic()

                if now - fps_start >= 1.0:
                    self.fps_ready.emit(
                        emitted_frames / (now - fps_start)
                    )
                    emitted_frames = 0
                    fps_start = now

        finally:
            cap.release()
            self.status_ready.emit("CAMERA STOPPED")


class PoseThread(QThread):

    detection_ready = Signal(dict)
    status_ready = Signal(str)

    def __init__(self, buffer, interval=0.075):
        super().__init__()
        self.buffer = buffer
        self.interval = interval
        self.running = True
        self.detector = MovementDetector()

    def stop(self):
        self.running = False
        if self.isRunning():
            self.wait(5000)

    def run(self):
        try:
            pose = PoseDetector()
        except Exception as exc:
            self.status_ready.emit(f"POSE MODEL ERROR: {exc}")
            return

        self.status_ready.emit("POSE ENGINE ONLINE")

        last_sequence = -1
        last_run = 0.0

        try:
            while self.running:
                now = time.monotonic()

                if now - last_run < self.interval:
                    self.msleep(2)
                    continue

                frame, sequence = self.buffer.read()

                if frame is None or sequence == last_sequence:
                    self.msleep(2)
                    continue

                # Process the newest frame, never a queue of old frames.
                small = cv2.resize(
                    frame,
                    (320, 240),
                    interpolation=cv2.INTER_AREA
                )

                _, landmarks = pose.process(small)

                if landmarks is None:
                    self.buffer.set_points(None)
                else:
                    points = [
                        (float(lm.x), float(lm.y))
                        if lm.visibility >= 0.50 else None
                        for lm in landmarks.landmark
                    ]
                    self.buffer.set_points(points)

                result = self.detector.update(
                    landmarks,
                    time.monotonic()
                )

                self.detection_ready.emit(result)

                last_sequence = sequence
                last_run = time.monotonic()

        finally:
            pose.close()


class MonitoringWorker(QThread):

    frame_ready = Signal(QImage)
    detection_ready = Signal(dict)
    status_ready = Signal(str)
    fps_ready = Signal(float)

    def __init__(
        self,
        camera_index=0,
        inference_interval=0.075,
        parent=None
    ):
        super().__init__(parent)

        self.camera_index = camera_index
        self.inference_interval = inference_interval

        self.running = True
        self.buffer = FrameBuffer()

        self.capture = None
        self.pose = None

    def stop(self):
        self.running = False

        if self.capture and self.capture.isRunning():
            self.capture.stop()

        if self.pose and self.pose.isRunning():
            self.pose.stop()

        if self.isRunning():
            self.wait(5000)

    def run(self):
        self.capture = CaptureThread(
            self.buffer,
            self.camera_index
        )

        self.pose = PoseThread(
            self.buffer,
            self.inference_interval
        )

        self.capture.frame_ready.connect(self.frame_ready)
        self.capture.status_ready.connect(self.status_ready)
        self.capture.fps_ready.connect(self.fps_ready)

        self.pose.detection_ready.connect(self.detection_ready)
        self.pose.status_ready.connect(self.status_ready)

        self.capture.start()
        self.pose.start()

        try:
            while (
                self.running
                and self.capture.isRunning()
                and self.pose.isRunning()
            ):
                self.msleep(20)

        finally:
            self.running = False

            if self.capture.isRunning():
                self.capture.stop()

            if self.pose.isRunning():
                self.pose.stop()
