import cv2

PARAMS_WINDOW = "Params"


class Param():
    def __init__(self, val=None) -> None:
        self.val = val

    def get_value(self):
        if self.val is not None:
            return self.val
        raise "no value"


def nothing(x): pass


class TrackbarParam(Param):
    def __init__(self, value_name, window_name: str, from_, to_) -> None:
        super().__init__(None)
        self.value_name, self.window_name = value_name, window_name
        self.from_, self.to_ = from_, to_
        self.created = False

    def get_value(self):
        if not self.created:
            cv2.createTrackbar(self.value_name, self.window_name,
                               self.from_, self.to_, nothing)
            self.created = True
        return cv2.getTrackbarPos(self.value_name, self.window_name)


class CheckBoxParam(TrackbarParam):
    def __init__(self, value_name, window_name: str, val=False) -> None:
        val = int(val)
        super().__init__(value_name, window_name, val, 1)

    def get_value(self):
        return bool(super().get_value())


def spawn_params_window(name=PARAMS_WINDOW, w=500, h=100):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, w, h)
