from core.event_logger import EventLogger

def test_event_persistence_and_export(tmp_path):
    logger=EventLogger(tmp_path/"events.sqlite3")
    logger.log("TEST","NORMAL","VERIFYING","unit test")
    rows=logger.list_events()
    assert rows and rows[0][1]=="TEST"
    out=tmp_path/"events.csv"
    logger.export_csv(out)
    assert out.exists()
    assert "timestamp" in out.read_text(encoding="utf-8")
