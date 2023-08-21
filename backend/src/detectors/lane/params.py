from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params: dict = {
    "Use np.fitpoly": True,
    "Car_center": 120,
    "Lane threshold": 100,
    "Weights": r".\backend\models\lane\train4\best.pt",
}
_default_types: dict = {
    "Use np.fitpoly": [str2bool],
    "Car_center": [float, int],
    "Lane threshold": [float, int],
    "Weights": [str],
}


class YoloLaneDetecorParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def USE_POLY_FIT(self): return self.get_porperty("Use np.fitpoly")

    @property
    def CAR_CENTER(self): return self.get_porperty("Car_center")
    @CAR_CENTER.setter
    def CAR_CENTER(self, value): return self.set("Car_center", value)

    @property
    def LANE_THRESHOLD(self): return self.get_porperty("Lane threshold")

    @property
    def WEIGHTS(self): return self.get_porperty("Weights")
    @WEIGHTS.setter
    def WEIGHTS(self, value): return self.set("Weights", value)
