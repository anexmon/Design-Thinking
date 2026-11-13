from core.emergency_manager import EmergencyManager

def test_verification_cancel_and_reset():
    m = EmergencyManager(15)
    assert m.update_detection(True, now=10) == ("NORMAL","VERIFYING")
    assert m.remaining(now=12) == 13
    assert m.cancel() == ("VERIFYING","CANCELLED")
    assert m.reset() == ("CANCELLED","NORMAL")

def test_countdown_escalates_once():
    m = EmergencyManager(15)
    m.update_detection(True, now=10)
    assert m.tick(now=24.9) is None
    assert m.tick(now=25) == ("VERIFYING","ESCALATED")
    assert m.tick(now=26) is None
