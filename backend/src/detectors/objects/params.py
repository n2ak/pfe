from src.base.params import ParamsBase

F = 2800
FOCAL_LENGTH = 4.74
_default_params: dict = {
    "f": F,
    "focal_length": FOCAL_LENGTH,
    "frame_center_y": 1,
    "yolo_version": "yolov5nu.pt",
    "car_min_distance": 40.0,
}
_default_types: dict = {
    "f": [float, int],
    "focal_length": [float],
    "frame_center_y": [float, int],
    "yolo_version": [str],
    "car_min_distance": [float],
}


class ObjectDetectorParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def F(self): return self.get_porperty("f")
    @property
    def FOCAL_LENGTH(self): return self.get_porperty("focal_length")
    @property
    def FRAME_CENTER_Y(self): return self.get_porperty("frame_center_y")
    @property
    def RENDER_CAR_BOX(self): return self.get_porperty("renderCarBox")
    @property
    def WEIGHTS(self): return self.get_porperty("yolo_version")
    @property
    def CAR_MIN_DISTANCE(self): return self.get_porperty("car_min_distance")
