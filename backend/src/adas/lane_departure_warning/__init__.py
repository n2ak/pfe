from src.base.system import ADASystem
from src.detectors.lane import YoloLaneDetecor


class LaneDepartureWarningSystem(ADASystem):
    def __init__(self, params) -> None:
        super().__init__("lane")
        self.model = YoloLaneDetecor(
            params=params,
        )

    def init(self, initial_frame):
        self.model.init(initial_frame)

    def _tick(self, frame):
        return self.model.pipeline(frame)

    def _draw(self, frame, draw_params):
        return self.model.draw(frame, draw_params)

    def _is_safe(self):
        return self.model.is_safe()

    def update_state(self, data):
        return self.model._update(data)

    def report(self):
        return ""
        text = f"""
Lane Departure Warning System:
        """

        return text
