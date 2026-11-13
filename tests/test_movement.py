from core.movement_detector import MovementDetector

class LM:
    def __init__(self,x,y,visibility=1.0):
        self.x=x; self.y=y; self.visibility=visibility
class Pose:
    def __init__(self,coords):
        self.landmark=[LM(0,0,0) for _ in range(33)]
        for i,(x,y) in coords.items(): self.landmark[i]=LM(x,y)

def test_no_pose_is_safe():
    d=MovementDetector()
    assert d.update(None, timestamp=1)["unusual"] is False

def test_first_pose_does_not_trigger():
    d=MovementDetector()
    coords={11:(.4,.3),12:(.6,.3),15:(.3,.5)}
    result=d.update(Pose(coords),timestamp=1)
    assert result["unusual"] is False
