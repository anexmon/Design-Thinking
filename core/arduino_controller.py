class ArduinoController:
    def __init__(self):
        self.serial = None
        self.port = None

    @staticmethod
    def available_ports():
        try:
            from serial.tools import list_ports
            return [p.device for p in list_ports.comports()]
        except Exception:
            return []

    @property
    def connected(self):
        return self.serial is not None and self.serial.is_open

    def connect(self, port, baud=9600):
        self.disconnect()
        import serial
        self.serial = serial.Serial(port, baud, timeout=1, write_timeout=1)
        self.port = port
        return True

    def send_state(self, state):
        if not self.connected:
            return False
        command = {"NORMAL": "NORMAL", "VERIFYING": "WARNING",
                   "CANCELLED": "NORMAL", "ESCALATED": "EMERGENCY"}.get(state, "NORMAL")
        try:
            self.serial.write((command + "\n").encode("ascii"))
            return True
        except Exception:
            self.disconnect()
            return False

    def disconnect(self):
        if self.serial:
            try:
                if self.serial.is_open:
                    self.serial.close()
            except Exception:
                pass
        self.serial = None
        self.port = None
