import cv2
from utils import to_numpy, show_window, is_window_closed


class Visualizer:
    def __init__(self, **kwargs) -> None:
        self.params = kwargs

    def start(self):
        self.init()

    def update_params(self, **kwargs):
        self.params.update(kwargs)

    def is_ready(self):
        return self._ready

    def show(self, *args):
        raise NotImplementedError()

    def stop(self, *args):
        raise NotImplementedError()

    def should_stop(self, *args):
        raise NotImplementedError()


class WindowVisualizer(Visualizer):
    window_name = 'main_window'
    close_key = 27  # ESC

    def init(self):
        self.window = cv2.namedWindow(self.window_name, cv2.WINDOW_FREERATIO)
        self._ready = True

    def stop(self):
        cv2.destroyAllWindows()

    def show(self, frame):
        import numpy as np
        frame = to_numpy(frame).astype(np.uint8)
        show_window(self.window_name, frame)

    def should_stop(self,):
        key = cv2.waitKey(1)
        return key == self.close_key or is_window_closed(self.window_name)


class ServerVisualizer(Visualizer):
    def init(self):
        from server.server import run_server
        import threading
        params = self.params
        host, port = params["host"], params["port"]
        program = params["program"]
        t = threading.Thread(target=run_server, args=(host, port, program))
        t.daemon = True
        t.start()

    def _ready(self):
        from server.server import has_started
        return has_started()

    def show(self, frame):
        from server.server import set_frame
        return set_frame(frame)

    def should_stop(self, *args):
        from server.server import has_stopped
        return has_stopped()

    def stop(self):
        pass
