from src.base.params import ParamsBase

_default_params: dict = {
    "car_center": 120,
    "lane_threshold": 1,
    "weights": r"F:\Master\S4\main\backend\models\train4\best.pt",
}


class YoloLaneDetecorParams(ParamsBase):
    def __init__(self, params: dict = _default_params) -> None:
        super().__init__(params)

    @property
    def CAR_CENTER(self): self.get_porperty("car_center")
    @property
    def LANE_THRESHOLD(self): self.get_porperty("lane_threshold")
    @property
    def WEIGHTS(self): self.get_porperty("weights")
