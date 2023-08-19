from src.base.params import ParamsBase
import typing
from src.adas import ADASystem


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


class ProcessorParams(ParamsBase):
    def __init__(self, systems: typing.List[ADASystem], initial_value: bool) -> None:
        params = {}
        types = {}
        for system in systems:
            name = system.name
            params[name] = initial_value
            types[name] = [str2bool]
        super().__init__(params, types)
