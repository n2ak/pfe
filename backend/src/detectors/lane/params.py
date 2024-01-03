from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params: dict = {
    "Use np.fitpoly": True,
    "Use polynome offset": False,
    "Polynome offset": 300,
    "Car center": 120,
    "Lane threshold": 100,
    "Weights": r".\backend\models\lane\train4\best.pt",
}
_default_types: dict = {
    "Use np.fitpoly": [str2bool],
    "Use polynome offset": [str2bool],
    "Polynome offset": [float, int],
    "Car center": [float, int],
    "Lane threshold": [float, int],
    "Weights": [str],
}


class YoloLaneDetecorParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def USE_POLY_FIT(self): return self.get_porperty("Use np.fitpoly")
    @USE_POLY_FIT.setter
    def USE_POLY_FIT(self, value): return self.set("Use np.fitpoly", value)

    @property
    def USE_POLY_OFFSET(self): return self.get_porperty("Use polynome offset")

    @USE_POLY_OFFSET.setter
    def USE_POLY_OFFSET(self, value): return self.set(
        "Use polynome offset", value)

    @property
    def POLY_OFFSET(self): return self.get_porperty("Polynome offset")
    @POLY_OFFSET.setter
    def POLY_OFFSET(self, value): return self.set("Polynome offset", value)

    @property
    def CAR_CENTER(self): return self.get_porperty("Car center")
    @CAR_CENTER.setter
    def CAR_CENTER(self, value): return self.set("Car center", value)

    @property
    def LANE_THRESHOLD(self): return self.get_porperty("Lane threshold")
    @LANE_THRESHOLD.setter
    def LANE_THRESHOLD(self, value): return self.set("Lane threshold", value)

    @property
    def WEIGHTS(self): return self.get_porperty("Weights")
    @WEIGHTS.setter
    def WEIGHTS(self, value): return self.set("Weights", value)
