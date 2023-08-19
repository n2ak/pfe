from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params = {
    "renderLines": False,
    "renderLane": False,
    "renderCarBox": True,
    "renderCenter": False,
}
_default_types: dict = {
    "renderLines": [str2bool],
    "renderLane": [str2bool],
    "renderCarBox": [str2bool],
    "renderCenter": [str2bool],
}


class DrawParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def RENDER_LINES(self): return self.get_porperty("renderLines")
    @RENDER_LINES.setter
    def RENDER_LINES(self, value): self.set("renderLines", value)

    @property
    def RENDER_LANE(self): return self.get_porperty("renderLane")
    @RENDER_LANE.setter
    def RENDER_LANE(self, value): self.set("renderLane", value)

    @property
    def RENDER_CAR_BOX(self): return self.get_porperty("renderCarBox")
    @RENDER_CAR_BOX.setter
    def RENDER_CAR_BOX(self, value): self.set("renderCarBox", value)

    @property
    def RENDER_CENTER(self): return self.get_porperty("renderCenter")
    @RENDER_CENTER.setter
    def RENDER_CENTER(self, value): self.set("renderCenter", value)
