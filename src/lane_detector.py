
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import *

N_WINDOWS = 10
MARGIN = 100
RECENTER_MINPIX = 50
SHOW_WINDOWS = True


class LaneDetector:

    def __init__(
        self,
        img_shape,
        use_bitwise=True,
        draw_roi=False,
        show_perp_lines=False,
        color_threshold=100,
        window_size_ratio=1,
        use_canny=False,
        canny_thresholds=(100, 300),
    ) -> None:
        self.H, self.W = img_shape
        self.use_bitwise = use_bitwise
        self.draw_roi = draw_roi
        self.show_perp_lines = show_perp_lines
        self.color_threshold = color_threshold
        self.window_size_ratio = window_size_ratio
        self.use_canny = use_canny
        self.canny_thresholds = canny_thresholds

    def init_polygon(self, config: dict = {}):
        polygon_height = config.get("polygon_height", 300)
        lane_center1 = config.get("lane_center1", 585), self.H - polygon_height
        lane_width1 = config.get("lane_width1", 250)
        lane_center2 = config.get("lane_center2", 638), self.H
        print(lane_center2)
        lane_width2 = config.get("lane_width2", 800)
        # polygon_length2 = 400
        # polygon_length2 = 100
        polygon = []
        polygon.append((lane_center1[0]-lane_width1//2, lane_center1[1]))
        polygon.append((lane_center1[0]+lane_width1//2, lane_center1[1]))
        polygon.append((lane_center2[0]+lane_width2//2, lane_center2[1]))
        polygon.append((lane_center2[0]-lane_width2//2, lane_center2[1]))
        polygon = np.array(polygon)
        self.polygon = np.array([polygon], dtype=np.int32)

    def trackbar(self, title: str, window: str, on_change):
        return cv2.createTrackbar(title, window, 19, 100, on_change)

    def pipeline(self, frame):
        # frame = cv2.resize(frame, (self.W, self.H))
        original_image = frame.copy()
        result = warp_perspective(frame, (self.H, self.W), self.polygon)

        image_warped = result.copy()
        if not self.use_canny:
            result = threshold(result, thresh=self.color_threshold)
            result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
        else:
            result = canny(
                result, self.canny_thresholds[0], self.canny_thresholds[1])

        if self.show_perp_lines:
            self.show_window("show_perp_lines", result, self.window_size_ratio)

        # show_img(result, cmap="gray")
        # hist = hi stogram(result//255)

        xs, ys = get_curvatures(result, RECENTER_MINPIX)
        result = draw_lane_zone(np.zeros_like(
            image_warped) if self.use_bitwise else image_warped, xs, ys, 50)
        # pass
        result = warp_perspective(
            (result), (self.H, self.W), self.polygon, flip=True)

        result = combine(result, original_image, use_bitwise=self.use_bitwise)

        if self.draw_roi:
            result = draw_polygon(result, self.polygon[0])

        return result

    def is_in_lane(self):
        return True

    def show_window(self, name, image, ratio=1):
        if not SHOW_WINDOWS:
            return

        if self.window_size_ratio != 1:
            size = int(image.shape[1]//ratio), int(image.shape[0]//ratio)
            image = cv2.resize(image, size)
        cv2.imshow(name, image)

    def put_text(self, frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=(100, 255, 0), **kwargs):
        cv2.putText(frame, text, org, font, scale, color, **kwargs)
