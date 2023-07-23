from base import ParamsBase
F = 2800
FOCAL_LENGTH = 4.74
_default_params: dict = {
    "f": F,
    "focal_length": FOCAL_LENGTH,
    "frame_center_y": 1,
    "renderCarBox": False,
    "yolo_version": "yolov5",

    "car_min_distance": 30,
    "car_avg_width": 2.5,
}


class CarParams(ParamsBase):
    def __init__(self, params: dict = _default_params) -> None:
        super().__init__(params)

    @property
    def f(self): return self.get_porperty("f")
    @property
    def focal_length(self): return self.get_porperty("focal_length")
    @property
    def frame_center_y(self): return self.get_porperty("frame_center_y")
    @property
    def renderCarBox(self): return self.get_porperty("renderCarBox")
    @property
    def yolo_version(self): return self.get_porperty("yolo_version")
    @property
    def car_min_distance(self): return self.get_porperty("car_min_distance")
    @property
    def car_avg_width(self): return self.get_porperty("car_avg_width")
