class ParamsBase:
    def __init__(self, params: dict) -> None:
        self.PARAMS = params

    def update_from_json(self, data: dict):
        for k in data.keys():
            if k not in self.PARAMS.keys():
                raise KeyError(
                    f"${self.__class__.__name__} , Unknown key: {k}")
            self.PARAMS[k] = data[k]
        import json
        print("Update params:")
        print(json.dumps(self.PARAMS, sort_keys=True, indent=4))

    def get_porperty(self, name):
        assert name in self.PARAMS.keys()
        return self.PARAMS[name]
