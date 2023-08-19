from src.base.params import ParamsBase

F = 2800
FOCAL_LENGTH = 4.74
_default_params: dict = {
    "f": F,
    "frame_center_y": 1,
    "yolo_version": "yolov5nu.pt",
    "car_min_distance": 40.0,
}
_default_types: dict = {
    "f": [float, int],
    "frame_center_y": [float, int],
    "yolo_version": [str],
    "car_min_distance": [float],
}


class ObjectDetectorParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def F(self): return self.get_porperty("f")
    @F.setter
    def F(self, value): self.set("f", value)

    @property
    def FRAME_CENTER_Y(self): return self.get_porperty("frame_center_y")
    @FRAME_CENTER_Y.setter
    def FRAME_CENTER_Y(self, value): self.set("frame_center_y", value)

    @property
    def WEIGHTS(self): return self.get_porperty("yolo_version")
    @WEIGHTS.setter
    def WEIGHTS(self, value): self.set("yolo_version", value)

    @property
    def CAR_MIN_DISTANCE(self): return self.get_porperty("car_min_distance")
    @CAR_MIN_DISTANCE.setter
    def CAR_MIN_DISTANCE(self, value): self.set("car_min_distance", value)
