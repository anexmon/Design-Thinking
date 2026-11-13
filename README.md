# Emergency Monitor Desktop

A Windows desktop prototype for camera-based pose tracking, experimental movement-anomaly flagging, a 15-second user verification workflow, event logging, and optional Arduino LED status output.

**Safety note:** This is an experimental movement-anomaly prototype, not a medically validated seizure detector. It does not contact hospitals, call emergency services, or provide medical advice. Any hospital indicator is explicitly simulated.

## Requirements
- Windows 10/11
- Python 3.11 (recommended; MediaPipe compatibility varies by Python version)
- Webcam
- Optional Arduino Uno R3 and LEDs

## Install and run (PowerShell)
```powershell
cd path\to\Emergency_Monitor_Desktop
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Tests
```powershell
pytest -v
```

## Arduino wiring
- Red LED anode -> 220Ω resistor -> D8
- Green LED anode -> 220Ω resistor -> D9
- Both LED cathodes -> GND
- Arduino connected to laptop by USB

Open `arduino/emergency_leds.ino` in Arduino IDE, select Arduino Uno and the correct COM port, then upload. In the desktop app open Hardware and select the same COM port.

Serial commands are `NORMAL`, `WARNING`, and `EMERGENCY`.
- NORMAL: green on
- WARNING: red blinking
- EMERGENCY: red solid

## Notes
- If no webcam is available, the app stays open and reports the camera error.
- If Arduino is unavailable, software monitoring continues without LED output.
- The initial detector uses conservative heuristics and requires calibration in realistic conditions. It may produce false positives and false negatives.
- The countdown uses monotonic time and is not based on UI animation timing.
