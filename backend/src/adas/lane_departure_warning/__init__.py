from src.base.system import ADASystem
from src.detectors.lane import YoloLaneDetecor


class LaneDepartureWarningSystem(ADASystem):
    def __init__(self, params) -> None:
        super().__init__("lane")
        self.model = YoloLaneDetecor(params=params)

    def _stop(self):
        pass

    def _init(self, initial_frame):
        self.shape = initial_frame.shape
        self.model.init(initial_frame)

    def _warmup(self):
        import numpy as np
        dummy_frame = np.zeros(self.shape)
        self.model.pipeline(dummy_frame)

    def _tick(self, frame):
        return self.model.pipeline(frame)

    def _draw(self, frame, draw_params):
        return self.model.draw(frame, draw_params)

    def _is_safe(self):
        return self.model.is_safe()

    def update_state(self, data):
        return self.model._update(data)

    def report(self):
        text = f"""
        Lane Departure Warning System:
            pos: {self.model.pos} > {self.model.params.LANE_THRESHOLD}
        """

        return text

    def ready(self):
        return self.model._ready
