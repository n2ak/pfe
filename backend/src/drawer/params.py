from base import ParamsBase

_default_params = {
    "renderLines": False,
    "renderLane": False,
    "renderCarBox": False,
}


class DrawParams(ParamsBase):
    def __init__(self, params: dict = _default_params) -> None:
        super().__init__(params)

    @property
    def renderLines(self): self.get_porperty("renderLines")
    @property
    def renderLane(self): self.get_porperty("renderLane")
    @property
    def renderCarBox(self): self.get_porperty("renderCarBox")
