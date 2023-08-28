from .sound import Sound
from src.adas import ADASystem
from .params import WarnerParams
from src.base.parameterizable import Parameterizable


class Warner(Parameterizable):
    def __init__(self, filepath, params=WarnerParams()) -> None:
        super().__init__("warn")
        self.sound = Sound(filepath=filepath)
        self.params = params

    def warn(self, source: ADASystem):
        if self.params.USE_SOUND:
            self.sound.start()
        elif self.sound.is_on:
            self.stop()
        if self.params.USE_LOG:
            print("Warning: car is not safe:", source.report())

    def stop(self):
        # if self.params.USE_SOUND:
        self.sound.stop()
