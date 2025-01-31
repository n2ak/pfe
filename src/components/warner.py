from src.sound import Sound
from src.adas import ADASystem
from src.base.parameterizable import Parameterizable
from src.base.params import ParamsBase, BooleanParam


class WarnerParams(ParamsBase):

    @staticmethod
    def _default(USE_SOUND=False, USE_LOG=False):
        params = [
            BooleanParam("USE_SOUND", "", USE_SOUND),
            BooleanParam("USE_LOG", "Draw lane", USE_LOG),
        ]
        return WarnerParams(
            params
        )

    @property
    def USE_SOUND(self): return self.get("USE_SOUND")

    @property
    def USE_LOG(self): return self.get("USE_LOG")


class Warner(Parameterizable):
    def __init__(self, filepath, params: WarnerParams) -> None:
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
