from typing_extensions import Self


class ParamBase:
    def __init__(self, name, desc, default_value):
        self.name = name
        self.desc = desc
        self.__val = default_value

    def value(self):
        return self.__val

    def set_value(self, v):
        v = self.parse_value(v)
        self.__val = v


class ParamsBase:
    def __init__(self, params: list[ParamBase]) -> None:
        self.inner = {p.name: p for p in params}

    @classmethod
    def default(cls, **kwargs) -> Self:
        return cls._default(**kwargs)

    def get(self, name) -> ParamBase:
        return self.inner[name]


class BooleanParam(ParamBase):

    def parse_value(self, v):
        return str2bool(v)


def str2bool(v):
    v = str(v)
    return v.lower() in ("yes", "true", "t", "1")


class IntParam(ParamBase):
    max_val = 500

    def parse_value(self, v):
        return int(v)


class StrParam(ParamBase):
    pass
