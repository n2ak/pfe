
import cv2
from src.base.lane_detector import LaneDetectorBase
from src.utils_ import *
from src.param import *
import numpy as np
from typing import Tuple

N_WINDOWS = 10
MARGIN = 100
RECENTER_MINPIX = 50
SHOW_WINDOWS = True


class MlLaneDetector(LaneDetectorBase):

    def __init__(
        self,
        img_shape,
        use_bitwise: CheckBoxParam = True,
        draw_roi: CheckBoxParam = False,
        show_perp_lines=False,
        color_threshold: TrackbarParam = 100,
        window_size_ratio=1,
        use_canny: CheckBoxParam = False,
        canny_thresholds: Tuple[TrackbarParam, TrackbarParam] = (100, 300),
    ) -> None:
        super().__init__()
        self.H, self.W = img_shape
        self.use_bitwise = use_bitwise
        self.draw_roi = draw_roi
        self.show_perp_lines = show_perp_lines
        self.color_threshold = color_threshold
        self.window_size_ratio = window_size_ratio
        self.use_canny = use_canny
        self.canny_thresholds = canny_thresholds

    def init_polygon(self, config: dict = {}):
        self.polygon = init_polygon(config, self.H)

    def trackbar(self, title: str, window: str, on_change):
        return cv2.createTrackbar(title, window, 19, 100, on_change)

    def draw(self, frame):
        # image_warped, xs, ys = info
        import time
        # time.(.1)
        # result = draw_lane_zone(np.zeros_like(
        #     self.image_warped) if self.use_bitwise else self.image_warped, self.xs, self.ys, 50)
        if self.draw_roi.get_value():
            result = draw_polygon(frame, self.polygon[0])
        # print("warped", dir(self))
        use_bitwise = self.use_bitwise.get_value()
        result = draw_lane_zone(
            np.zeros_like(
                self.image_warped) if use_bitwise else self.image_warped,
            self.xs,
            self.ys,
            50
        )
        result = warp_perspective(
            (result), (self.H, self.W), self.polygon, flip=True)
        result = combine(result, frame, use_bitwise=use_bitwise)
        return result

    def pipeline(self, frame):

        self.detected_lines = False
        result = warp_perspective(frame, (self.H, self.W), self.polygon)
        self.image_warped = None
        self.image_warped = result.copy()
        # TODO: add gaussian blur
        # TODO: use equalize_hist
        # TODO: use dilate
        if not self.use_canny.get_value():
            result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
            result = dilate(result, iterations=1)
            result = threshold(result, thresh=self.color_threshold)
        else:
            result = canny(
                result, self.canny_thresholds[0].get_value(), self.canny_thresholds[1].get_value())
        self.lines = result.copy()
        lanes = get_curvatures(result, RECENTER_MINPIX)
        if lanes is not None:
            self.detected_lines = True
            self.radiuses, self.xs, self.ys = lanes

    def is_in_lane(self):
        r_left, r_right = self.radiuses
        # print(self.radiuses)
        th = 900  # TODO make it a Param
        return not (r_left < th or r_right < th)
