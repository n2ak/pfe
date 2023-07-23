import threading
class Params:
    def __init__(self, default:dict={
        "renderLines": False,
        "renderLane": False,
        "renderCarBox": False,
    }) -> None:
        self.lock = threading.Lock()
        self.PARAMS = default

    def get_porperty(self,name):
        assert name in self.PARAMS.keys()
        with self.lock:
            return self.PARAMS[name]

    @property 
    def renderLines(self): return self.get_porperty("renderLines")
    @property
    def renderLane(self): return self.get_porperty("renderLane")
    @property
    def renderCarBox(self): return self.get_porperty("renderCarBox")

    def update_from_json(self,data:dict):
        with self.lock:
            for k in data.keys():
                if k not in self.PARAMS.keys():
                   raise KeyError(f"Unknown key: {k}") 
                self.PARAMS[k] = bool(data[k])


