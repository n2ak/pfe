from src.base.params import ParamsBase

_default_params = {
    "renderLines": False,
    "renderLane": False,
    "renderCarBox": False,
}


class DrawParams(ParamsBase):
    def __init__(self, params: dict = _default_params) -> None:
        super().__init__(params)

    @property
    def RENDER_LINES(self): return self.get_porperty("renderLines")
    @property
    def RENDER_LANE(self): return self.get_porperty("renderLane")
    @property
    def RENDER_CAR_BOX(self): return self.get_porperty("renderCarBox")
