from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params = {
    "Draw Lines": True,
    "Draw Lane": False,
    "Draw Object Box": True,
    "Draw car center": True,
    "Lane: Number of points": 20,
}
_default_types: dict = {
    "Draw Lines": [str2bool],
    "Draw Lane": [str2bool],
    "Draw Object Box": [str2bool],
    "Draw car center": [str2bool],
    "Lane: Number of points": [float, int],
}


class DrawParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def RENDER_LINES(self): return self.get_porperty("Draw Lines")
    @RENDER_LINES.setter
    def RENDER_LINES(self, value): self.set("Draw Lines", value)

    @property
    def RENDER_LANE(self): return self.get_porperty("Draw Lane")
    @RENDER_LANE.setter
    def RENDER_LANE(self, value): self.set("Draw Lane", value)

    @property
    def RENDER_CAR_BOX(self): return self.get_porperty("Draw Object Box")
    @RENDER_CAR_BOX.setter
    def RENDER_CAR_BOX(self, value): self.set("Draw Object Box", value)

    @property
    def RENDER_CENTER(self): return self.get_porperty("Draw car center")
    @RENDER_CENTER.setter
    def RENDER_CENTER(self, value): self.set("Draw car center", value)

    @property
    def LANE_N_POINTS(self): return self.get_porperty("Lane: Number of points")
