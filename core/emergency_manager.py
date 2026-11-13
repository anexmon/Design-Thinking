import time
from threading import RLock

class EmergencyManager:
    NORMAL = "NORMAL"
    VERIFYING = "VERIFYING"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"

    def __init__(self, verify_seconds=15):
        self.verify_seconds = verify_seconds
        self.state = self.NORMAL
        self.deadline = None
        self.lock = RLock()
        self._last_transition = None

    def update_detection(self, unusual, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            if self.state == self.NORMAL and unusual:
                self.state = self.VERIFYING
                self.deadline = now + self.verify_seconds
                self._last_transition = (self.NORMAL, self.VERIFYING)
                return self._last_transition
        return None

    def tick(self, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            if self.state == self.VERIFYING and self.deadline is not None and now >= self.deadline:
                old = self.state
                self.state = self.ESCALATED
                self.deadline = None
                self._last_transition = (old, self.ESCALATED)
                return self._last_transition
        return None

    def cancel(self):
        with self.lock:
            if self.state != self.VERIFYING:
                return None
            old = self.state
            self.state = self.CANCELLED
            self.deadline = None
            self._last_transition = (old, self.CANCELLED)
            return self._last_transition

    def reset(self):
        with self.lock:
            old = self.state
            self.state = self.NORMAL
            self.deadline = None
            self._last_transition = (old, self.NORMAL)
            return self._last_transition

    def remaining(self, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            if self.state != self.VERIFYING or self.deadline is None:
                return 0
            return max(0, self.deadline - now)
