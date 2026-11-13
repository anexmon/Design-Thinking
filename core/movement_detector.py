
from collections import deque
import math
import time


class MovementDetector:
    """
    Experimental multi-region movement anomaly detector.

    Ordinary isolated hand movements are filtered out.
    Requires sustained movement across multiple body regions.

    NOT a medical seizure detector.
    """

    REGIONS = {
        "left_arm": (13, 15),
        "right_arm": (14, 16),
        "torso": (11, 12, 23, 24),
        "legs": (25, 26, 27, 28),
    }

    def __init__(
        self,
        active_speed=1.8,
        extreme_speed=4.5,
        window_seconds=1.5,
        required_regions=2,
        required_samples=5
    ):
        self.active_speed = active_speed
        self.extreme_speed = extreme_speed
        self.window_seconds = window_seconds
        self.required_regions = required_regions
        self.required_samples = required_samples

        self.previous = {}
        self.samples = deque()

    def reset(self):
        self.previous.clear()
        self.samples.clear()

    def update(self, landmarks, timestamp=None):
        now = timestamp if timestamp is not None else time.monotonic()

        if landmarks is None:
            self.reset()
            return {
                "unusual": False,
                "speed": 0.0,
                "label": "NO POSE"
            }

        points = {}

        for idx in range(33):
            try:
                lm = landmarks.landmark[idx]

                if lm.visibility >= 0.50:
                    points[idx] = (float(lm.x), float(lm.y))
            except (AttributeError, IndexError):
                continue

        if 11 not in points or 12 not in points:
            self.previous.clear()
            self.samples.clear()
            return {
                "unusual": False,
                "speed": 0.0,
                "label": "TRACKING BODY"
            }

        # Use torso height as the reference scale.
        if 23 in points and 24 in points:
            hip_y = (points[23][1] + points[24][1]) / 2
            shoulder_y = (points[11][1] + points[12][1]) / 2
            body_scale = abs(hip_y - shoulder_y)
        else:
            body_scale = 0.0

        if body_scale < 0.05:
            body_scale = math.dist(points[11], points[12])

        body_scale = max(body_scale, 0.12)

        region_speeds = {}

        for region, indices in self.REGIONS.items():
            speeds = []

            for idx in indices:
                if idx not in points or idx not in self.previous:
                    continue

                old_time, old_point = self.previous[idx]
                dt = now - old_time

                if dt < 0.03 or dt > 0.75:
                    continue

                distance = math.dist(points[idx], old_point)
                speeds.append(distance / body_scale / dt)

            region_speeds[region] = max(speeds, default=0.0)

        self.previous = {
            idx: (now, point)
            for idx, point in points.items()
        }

        active_regions = sum(
            speed >= self.active_speed
            for speed in region_speeds.values()
        )

        extreme_regions = sum(
            speed >= self.extreme_speed
            for speed in region_speeds.values()
        )

        maximum_speed = max(region_speeds.values(), default=0.0)

        self.samples.append((
            now,
            active_regions,
            extreme_regions,
            maximum_speed
        ))

        while (
            self.samples
            and now - self.samples[0][0] > self.window_seconds
        ):
            self.samples.popleft()

        sustained_count = sum(
            regions >= self.required_regions
            for _, regions, _, _ in self.samples
        )

        extreme_count = sum(
            regions >= self.required_regions
            for _, _, regions, _ in self.samples
        )

        unusual = (
            len(self.samples) >= self.required_samples
            and (
                sustained_count >= self.required_samples
                or extreme_count >= 3
            )
        )

        if unusual:
            label = "UNUSUAL MOVEMENT"
        elif active_regions > 0:
            label = "ACTIVE MOVEMENT"
        else:
            label = "NORMAL MOVEMENT"

        return {
            "unusual": unusual,
            "speed": round(maximum_speed, 2),
            "label": label
        }
