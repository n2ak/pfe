
import time
import numpy as np
from .params import DrawParams
from src.adas import ADASystem
from typing import List


class Drawer():
    fps_ = [0]

    def __init__(self, params: DrawParams) -> None:
        self.params = params
        self.prev_time = time.time()-1

    def draw(self, frame, systems: List[ADASystem]):
        from src.utils_ import draw_text_with_backgraound
        for system in systems:
            frame = system.draw(frame, self.params)

        safe = all([system.is_safe() for system in systems])
        # safe = car_detector.safe and lane_detector.safe

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
        from src.utils_ import put_text

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

    def get_param(self, ret_types=True):
        params = self.params
        if ret_types:
            params = "drawing", params
        return params
