from src.base.params import ParamsBase

F = 2800
FOCAL_LENGTH = 4.74
_default_params: dict = {
    "f": F,
    "focal_length": FOCAL_LENGTH,
    "frame_center_y": 1,
    # "renderCarBox": False,
    "yolo_version": "yolov5nu.pt",

    "car_min_distance": 40.0,
    # "car_avg_width": 2.5,
}


class ObjectDetectorParams(ParamsBase):
    def __init__(self, params: dict = _default_params) -> None:
        super().__init__(params)

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
