
from .base import LaneDetectorBase


class YoloLaneDetecor(LaneDetectorBase):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.lane = None

    def draw(self, frame, lanes):
        return frame

    def pipeline(self, frame):
        return frame

    def is_in_lane(self):
        return True
