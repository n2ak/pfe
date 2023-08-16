from src.base.system import ADASystem
from src.detectors.lane import YoloLaneDetecor


class LaneDepartureWarningSystem(ADASystem):
    def __init__(self, car_center, lane_threshold) -> None:
        super().__init__()
        self.model = YoloLaneDetecor(
            CAR_CENTER=car_center,
            LANE_THRESHOLD=lane_threshold,
        )

    def tick(self, frame):
        return self.model.pipeline(frame)

    def draw(self, frame):
        return self.model.draw(frame)

    def is_safe(self):
        return self.model.is_safe()

    def update_state(self, data):
        return self.model._update(data)

    def report(self):
        return ""
        text = f"""
Lane Departure Warning System:
        """

        return text
