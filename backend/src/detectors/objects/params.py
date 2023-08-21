from src.base.params import ParamsBase

F = 2800
FOCAL_LENGTH = 4.74
_default_params: dict = {
    "Focal length in pixels": F,
    "Y frame center": 1,
    "Yolo version": "yolov5nu.pt",
    "Car minimum distance": 40.0,
}
_default_types: dict = {
    "Focal length in pixels": [float, int],
    "Y frame center": [float, int],
    "Yolo version": [str],
    "Car minimum distance": [float],
}


class ObjectDetectorParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def F(self): return self.get_porperty("Focal length in pixels")
    @F.setter
    def F(self, value): self.set("Focal length in pixels", value)

    @property
    def FRAME_CENTER_Y(self): return self.get_porperty("Y frame center")
    @FRAME_CENTER_Y.setter
    def FRAME_CENTER_Y(self, value): self.set("Y frame center", value)

    @property
    def WEIGHTS(self): return self.get_porperty("Yolo version")
    @WEIGHTS.setter
    def WEIGHTS(self, value): self.set("Yolo version", value)

    @property
    def CAR_MIN_DISTANCE(self): return self.get_porperty(
        "Car minimum distance")

    @CAR_MIN_DISTANCE.setter
    def CAR_MIN_DISTANCE(self, value): self.set("Car minimum distance", value)
