from src.base.params import ParamsBase
import typing


class Parameterizable:
    def __init__(self, path, name=None) -> None:
        if name is None:
            name = self.__class__.__name__
        self.path = path
        self.name = name

    def get_param(self, ret_type) -> typing.Union[ParamsBase, typing.Tuple[str, ParamsBase]]:
        try:
            params = self.model.params
        except:
            params = self.params

        if ret_type:
            return self.path, (self.name, params)
        return params
