
import time
import numpy as np
from .params import DrawParams


class Drawer():
    fps_ = [0]

    def __init__(self, params: DrawParams) -> None:
        self.params = params
        self.prev_time = time.time()-1

    def draw(self, frame, car_detector, lane_detector, cars, cars_safe, lanes, lanes_safe):
        from utils_ import draw_text_with_backgraound

        if cars_safe:
            if self.params.renderLane:
                frame = lane_detector.draw(frame, lanes)
        if self.params.renderCarBox:
            frame = car_detector.draw(frame, cars)

        safe = cars_safe and lanes_safe
        fps = self.update_fps()
        text = f"FPS: {int(fps)}\nSafe: {safe}"
        draw_text_with_backgraound(
            frame,
            text,
            7,
            90
        )
        return frame

    def update_fps(self, frame=None):
        from utils_ import put_text

        new = time.time()
        self.fps_.append(1//(new-self.prev_time))
        self.fps_ = self.fps_[-10:]
        # print(self.fps_)
        fps = np.mean(self.fps_)
        self.prev_time = new
        if frame is not None:
            text = f"FPS: {int(fps)}"
            put_text(frame, text, (7, 90), thickness=2)
        return fps