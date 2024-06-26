class ParamsBase:
    def __init__(self, params: dict, types) -> None:
        self.PARAMS = params
        self.types = types

    def update_from_json(self, data: dict):
        for k in data.keys():
            if k not in self.PARAMS.keys():
                raise KeyError(
                    f"${self.__class__.__name__} , Unknown key: {k}")
            value = data[k]
            value = self.parse(k, value)
            self.PARAMS[k] = value
        self.print()

    def print(self):
        print(self.__class__.__name__)
        import json
        print(json.dumps(self.PARAMS, sort_keys=True, indent=4))

    def set(self, key, value):
        value = self.parse(key, value)
        self.PARAMS[key] = value

    def parse(self, key, value):
        for convert in self.types[key]:
            value = convert(value)
        return value

    def get_porperty(self, name):
        assert name in self.PARAMS.keys(
        ), f"{name} not in {self.PARAMS.keys()}"
        return self.PARAMS[name]

    def update(self, PARAMS: dict):
        assert sorted(self.PARAMS.keys()) == sorted(PARAMS.keys())
        self.PARAMS = PARAMS
