
import cv2
import mediapipe as mp


class PoseDetector:
    """
    Lightweight MediaPipe pose detector for real-time monitoring.

    Returns pose landmarks for the monitoring worker.
    Skeleton rendering is handled by the camera thread.
    """

    def __init__(self):
        self.mp_pose = mp.solutions.pose

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False,
            min_detection_confidence=0.50,
            min_tracking_confidence=0.50
        )

    def process(self, frame):
        """
        Accepts a BGR OpenCV frame.
        Returns (frame, pose_landmarks).
        """

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.pose.process(rgb)

        return frame, results.pose_landmarks

    def close(self):
        if self.pose is not None:
            self.pose.close()
