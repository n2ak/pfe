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
    @property
    def RENDER_LANE(self): return self.get_porperty("renderLane")
    @property
    def RENDER_CAR_BOX(self): return self.get_porperty("renderCarBox")
    @property
    def RENDER_CENTER(self): return self.get_porperty("renderCenter")
