from src.base.params import ParamsBase


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


_default_params = {
    "Use sound": True,
    "Log": True,
}
_default_types: dict = {
    "Use sound": [str2bool],
    "Log": [str2bool],
}


class WarnerParams(ParamsBase):
    def __init__(self, params: dict = _default_params, types=_default_types) -> None:
        super().__init__(params, types)

    @property
    def USE_SOUND(self): return self.get_porperty("Use sound")
    @USE_SOUND.setter
    def USE_SOUND(self, value): self.set("Use sound", value)

    @property
    def USE_LOG(self): return self.get_porperty("Log")
    @USE_LOG.setter
    def USE_LOG(self, value): self.set("Log", value)
