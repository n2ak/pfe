import cv2
from src.utils import to_numpy, show_window, is_window_closed


class Visualizer:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def start(self):
        self.init()
        print("Visualizer has started.")

    def update_kwargs(self, **kwargs):
        self.kwargs.update(kwargs)

    def is_ready(self):
        return self._ready

    def show(self, *args):
        raise NotImplementedError()

    def stop(self, *args):
        raise NotImplementedError()

    def should_stop(self, *args):
        raise NotImplementedError()


class CheckBox:
    checked = False

    def __init__(self, x, y, w=20, h=20, label="", font=cv2.FONT_HERSHEY_COMPLEX, initial=False, onchange=None):
        self.coords = x, y, w, h
        self.label = label
        self.font = font
        self.onchange = onchange
        self.checked = bool(initial)
    # Callback function for mouse events

    def draw(self, img):
        x, y, w, h = self.coords
        if self.checked:
            color = (0, 255, 0)  # Green for checked
            cv2.line(img, (x, y), (x + w, y + h),
                     (0, 0, 0), 5)  # Draw a check mark
            cv2.line(img, (x + w, y), (x, y + h), (0, 0, 0), 5)
        else:
            color = (255, 255, 255)  # White for unchecked
        from utils import draw_text_with_backgraound
        draw_text_with_backgraound(img, self.label, x + w + 5, y)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        return img

    def mouse_callback(self, event, mousex, mousey, flags, param):
        x, y, w, h = self.coords
        if event == cv2.EVENT_LBUTTONDOWN:
            if x <= mousex <= x + w and y <= mousey <= y + h:
                self.checked = not self.checked
                if self.onchange is not None:
                    self.onchange(self.checked)


class WindowVisualizer(Visualizer):
    window_name = 'main_window'
    close_key = 27  # ESC
    _ready = False

    def mouse_callback(self, *args, **kwargs):
        for ui in self.uis:
            ui.mouse_callback(*args, **kwargs)

    def init(self):
        from src.base.params import BooleanParam, IntParam, StrParam
        from .program import Program

        window_name = self.window_name
        input_window_name = "Inputs"
        cv2.namedWindow(window_name, cv2.WINDOW_FREERATIO)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        cv2.namedWindow(input_window_name, cv2.WINDOW_GUI_NORMAL)
        program: Program = self.kwargs["program"]
        params = [p for p in program.processor.all_parameterizables()]
        self.uis = []
        y_start = 200

        def update(v, param: BooleanParam):
            param.set_value(v)
        for p in params:
            for k, v in p.inner.items():
                if isinstance(v, BooleanParam):
                    h = 20
                    self.uis.append(
                        CheckBox(10, y_start, h=h, label=v.desc, onchange=v.set_value, initial=v.value()))
                    y_start += h + 5
                elif isinstance(v, IntParam):
                    import functools
                    cv2.createTrackbar(v.desc, input_window_name,
                                       v.value(), v.max_val, functools.partial(update, param=v))
                elif isinstance(v, StrParam):
                    pass
                else:
                    assert False, type(v)
            y_start += 20

        self._ready = True

    def stop(self):
        cv2.destroyAllWindows()

    def show(self, frame):
        import numpy as np
        frame = to_numpy(frame).astype(np.uint8)
        for ui in self.uis:
            frame = ui.draw(frame)
        show_window(self.window_name, frame)

    def should_stop(self,):
        key = cv2.waitKey(1)
        return key == self.close_key or is_window_closed(self.window_name)


class ServerVisualizer(Visualizer):
    def init(self):
        from src.server import run_server
        import threading
        params = self.kwargs
        host, port = params["host"], params["port"]
        program = params["program"]
        t = threading.Thread(target=run_server, args=(host, port, program))
        t.daemon = True
        t.start()

    def _ready(self):
        from src.server import has_started
        return has_started()

    def show(self, frame):
        from src.server import set_frame
        return set_frame(frame)

    def should_stop(self, *args):
        from src.server import has_stopped
        return has_stopped()

    def stop(self):
        pass
