from src.base.params import ParamsBase, BooleanParam, IntParam, StrParam


class YoloLaneDetecorParams(ParamsBase):

    @staticmethod
    def _default(
        USE_POLY_FIT=True,
        USE_POLY_OFFSET=False,
        POLY_OFFSET=300,
        CAR_CENTER=120,
        LANE_THRESHOLD=100,
    ):
        params = [
            BooleanParam("USE_POLY_FIT", "Use poly fit.", USE_POLY_FIT),
            BooleanParam("USE_POLY_OFFSET",
                         "Use poly offset", USE_POLY_OFFSET),
            IntParam("POLY_OFFSET", "Poly offset.", POLY_OFFSET),
            IntParam("CAR_CENTER", "Car center", CAR_CENTER),
            IntParam("LANE_THRESHOLD", "Lane threshold", LANE_THRESHOLD),
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
