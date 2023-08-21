from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params = {
    "Render lines": True,
    "Render lane": False,
    "Render car box": True,
    "Render car center": True,
    "Lane: Number of points": 20,
}
_default_types: dict = {
    "Render lines": [str2bool],
    "Render lane": [str2bool],
    "Render car box": [str2bool],
    "Render car center": [str2bool],
    "Lane: Number of points": [float, int],
}


class DrawParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def RENDER_LINES(self): return self.get_porperty("Render lines")
    @RENDER_LINES.setter
    def RENDER_LINES(self, value): self.set("Render lines", value)

    @property
    def RENDER_LANE(self): return self.get_porperty("Render lane")
    @RENDER_LANE.setter
    def RENDER_LANE(self, value): self.set("Render lane", value)

    @property
    def RENDER_CAR_BOX(self): return self.get_porperty("Render car box")
    @RENDER_CAR_BOX.setter
    def RENDER_CAR_BOX(self, value): self.set("Render car box", value)

    @property
    def RENDER_CENTER(self): return self.get_porperty("Render car center")
    @RENDER_CENTER.setter
    def RENDER_CENTER(self, value): self.set("Render car center", value)

    @property
    def LANE_N_POINTS(self): return self.get_porperty("Lane: Number of points")
