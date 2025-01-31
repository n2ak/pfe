from src.base.params import ParamsBase


class Parameterizable:
    def __init__(self, name, params: ParamsBase) -> None:
        if name is None:
            name = self.__class__.__name__
        assert issubclass(params.__class__, ParamsBase), params
        self.params = params
        self.name = name

    def get_params(self) -> ParamsBase:
        return self.params
