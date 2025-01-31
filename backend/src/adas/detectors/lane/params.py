from src.base.params import ParamsBase, BooleanParam, IntParam, StrParam


class YoloLaneDetecorParams(ParamsBase):

    @staticmethod
    def _default():
        params = [
            BooleanParam("USE_POLY_FIT", "Use poly fit.", True),
            BooleanParam("USE_POLY_OFFSET", "Use poly offset", False),
            IntParam("POLY_OFFSET", "Poly offset.", 300),
            IntParam("CAR_CENTER", "Car center", 120),
            IntParam("LANE_THRESHOLD", "Lane threshold", 100),
            StrParam("WEIGHTS", "Model weights",
                     r"./models/lane/train4/best.pt"),
        ]
        return YoloLaneDetecorParams(
            params
        )

    @property
    def USE_POLY_FIT(self): return self.get("USE_POLY_FIT")

    @property
    def USE_POLY_OFFSET(self): return self.get("USE_POLY_OFFSET")

    @property
    def POLY_OFFSET(self): return self.get("POLY_OFFSET")

    @property
    def CAR_CENTER(self): return self.get("CAR_CENTER")

    @property
    def LANE_THRESHOLD(self): return self.get("LANE_THRESHOLD")

    @property
    def WEIGHTS(self): return self.get("WEIGHTS")
