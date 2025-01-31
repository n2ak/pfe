from typing_extensions import Self


class ParamBase:
    def __init__(self, name, desc, default_value):
        self.name = name
        self.desc = desc
        self.__val = default_value

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"{name}({self.__val})"

    def value(self):
        return self.__val

    def set_value(self, v):
        v = self.parse_value(v)
        self.__val = v

    def is_boolean(self):
        return isinstance(self, BooleanParam)


class ParamsBase:
    def __init__(self, params: list[ParamBase]) -> None:
        self.inner = {p.name: p for p in params}

    @classmethod
    def default(cls, **kwargs) -> Self:
        return cls._default(**kwargs)

    def get(self, name) -> ParamBase:
        return self.inner[name]

    def __repr__(self) -> str:
        name = self.__class__.__name__
        inner = "\n".join([f"\t{k}: {v}," for k, v in self.inner.items()])
        return f"{name}(\n{inner}\n)"

    def update_from_json(self, data: dict[str,]):
        for k, v in data.items():
            assert k in self.inner, f"'{type}' not in {self.inner.keys()}"
            self.inner[k].set_value(v)


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
