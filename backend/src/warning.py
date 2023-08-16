from src.sound import Sound
from src.adas import ADASystem


class Warner:
    def __init__(self, use_sound=True, log=True) -> None:

        self.sound = Sound()
        self.use_sound = use_sound
        self.log = log

    def warn(self, source: ADASystem):
        if self.use_sound:
            self.sound.start()
        if self.log:
            print("Warning: car is not safe:", source.report())

    def stop(self):
        if self.use_sound:
            self.sound.stop()
