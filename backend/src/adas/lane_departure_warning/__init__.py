from src.adas.adas_system import ADASystem
from src.adas.detectors.lane.yolo_detector import YoloLaneDetecor


class LaneDepartureWarningSystem(ADASystem):
    def __init__(self, params) -> None:
        super().__init__("lane", params)
        self.detector = YoloLaneDetecor(params=params)

    def _stop(self):
        pass

    def _init(self, initial_frame):
        self.shape = initial_frame.shape
        self.detector.init(initial_frame)

    def _warmup(self):
        import numpy as np
        dummy_frame = np.zeros(self.shape)
        self.detector.pipeline(dummy_frame)

    def _tick(self, frame):
        return self.detector.pipeline(frame)

    def _draw(self, frame, draw_params):
        return self.detector.draw(frame, draw_params)

    def _is_safe(self):
        return self.detector.is_safe()

    def update_state(self, data):
        return self.detector._update(data)

    def report(self):
        text = f"""
        Lane Departure Warning System:
            pos: {self.detector.pos} > {self.detector.params.LANE_THRESHOLD}
        """

        return text

    def ready(self):
        return self.detector._ready
