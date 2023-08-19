from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params: dict = {
    "use_poly_fit": True,
    "car_center": 120,
    "lane_threshold": 100,
    "weights": r".\backend\models\lane\train4\best.pt",
}
_default_types: dict = {
    "use_poly_fit": [str2bool],
    "car_center": [float, int],
    "lane_threshold": [float, int],
    "weights": [str],
}


class YoloLaneDetecorParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def USE_POLY_FIT(self): return self.get_porperty("use_poly_fit")

    @property
    def CAR_CENTER(self): return self.get_porperty("car_center")
    @CAR_CENTER.setter
    def CAR_CENTER(self, value): return self.set("car_center", value)

    @property
    def LANE_THRESHOLD(self): return self.get_porperty("lane_threshold")

    @property
    def WEIGHTS(self): return self.get_porperty("weights")
