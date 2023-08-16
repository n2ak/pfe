from src.detectors.lane.params import YoloLaneDetecorParams
import numpy as np
import cv2
from src.utils_ import draw_lane_zone
from src.detectors.lane import LaneDetectorBase
from src.yolo import Yolo

GREEN = np.array([0, 255, 0])/255
RED = np.array([255, 0, 0])/255


class YoloLaneDetecor(LaneDetectorBase):

    def __init__(
        self,
        params=YoloLaneDetecorParams(),
        # weights=r"F:\Master\S4\main\backend\models\train4\best.pt"
    ) -> None:
        super().__init__()
        self.model = Yolo(params.WEIGHTS, hub=False)
        self.lane = None

        self._ready = False
        self.in_lane = True

        self.params = params

    def draw(self, frame):
        h, w = frame.shape[:2]

        if not self._ready:
            return frame
        left, right, ys, in_lane = self.left, self.right, self.ys, self.in_lane
        left = scale(left, w)
        right = scale(right, w)
        ys = scale(ys, h)
        left_lane, right_lane, height = left[-1], right[-1], ys[-1]

        car_center, threshold = self.params.CAR_CENTER, self.params.LANE_THRESHOLD

        out = draw_lane_zone_transp(
            frame, left, right, ys, opacity=.30, color=(0, 1, 0))

        lane_center = (left_lane + right_lane) // 2

        ccr = car_center+threshold
        ccl = car_center-threshold
        ht = h - 40
        hm = h - 50
        hb = h - 60

        cv2.line(out, (ccr, hm), (ccl, hm), 0, 5)
        cv2.line(out, (ccr, hb), (ccr, ht), 0, 5)
        cv2.line(out, (ccl, hb), (ccl, ht), 0, 5)
        cv2.circle(out, (car_center, hm), 7, 0, -1)

        c = GREEN if in_lane else RED
        cv2.circle(out, (lane_center, height), 10, c, -1)
        return out

    def pipeline(self, frame):
        res = self.model.predict(frame)
        lines = get_lines(res.masks.data[:3])
        mask = np.zeros(frame.shape[:2])

        colors = [3, 2, 1]
        for i, o in enumerate(lines):
            draw_masks_on_image(mask, [zip(*o[::-1])], color=colors[i])

        left, right, ys, dirs = get_curvatures2(mask, [1, 2], 1, range=[0, -1])

        if len(left) == 0 or len(right) == 0:
            return None

        H, W = res.masks.data[0].shape
        left = normalize(left, W)
        right = normalize(right, W)
        ys = normalize(ys, H)

        left_lane, right_lane, height = left[-1], right[-1], ys[-1]

        pos, self.in_lane = lane_departure_warning(
            left_lane,
            right_lane,
            self.params.CAR_CENTER,
            self.params.LANE_THRESHOLD
        )

        return left, right, ys, self.in_lane

    def is_in_lane(self):
        return self.in_lane

    def _update(self, data):
        self._ready = True
        if data is None:
            self._ready = False
            return
        self.left, self.right, self.ys, self.in_lane = data

    def is_safe(self):
        return self.in_lane


def lane_departure_warning(left_lane, right_lane, car_center, threshold):
    lane_center = (left_lane + right_lane) // 2
    lateral_position = abs(car_center - lane_center)
    in_lane = lateral_position < threshold

    return lateral_position, in_lane


def normalize(var, by):
    if isinstance(var, list):
        return [var[i]/by for i in range(len(var))]
    return var/by


def scale(var, to):
    if isinstance(var, list):
        return [int(var[i]*to) for i in range(len(var))]
    return int(var*to)


def draw_lane_zone_transp(image, left, right, ys, opacity=.75, color=(0, 1, 0)):
    mask = draw_lane_zone(np.zeros_like(
        image), (right, left), ys, step=5).astype(np.float64)
    mask /= 255.0
    mask *= opacity
    green = np.ones(image.shape, dtype=np.float64)*color
    return green*mask + (image/255)*(1.0-mask)


def get_curvatures2(masks, indexes, step=3, range=[1, -2]):
    left, right, ys = [], [], []
    mid = []

    l, r = range
    for i, line in enumerate(masks[::step]):
        i = i * step
        ind1 = np.where(line == indexes[0])
        ind2 = np.where(line == indexes[1])
        ind1 = ind1[0]
        ind2 = ind2[0]
        if len(ind1) <= (l+1)*2 or len(ind2) <= (l+1)*2:
            continue
        mid1 = (ind1[l]+ind1[r])//2
        mid2 = (ind2[l]+ind2[r])//2
        left.append(mid1)
        right.append(mid2)

        ys.append(i)

        mid.append(((mid1+mid2)//2, i))
    return left, right, ys, mid


def draw_masks_on_image(image, lines, color=255):
    for line in lines:
        prev = None
        for x, y in line:
            curr = int(x), int(y)
            if prev is not None:
                cv2.line(image, prev, curr, color, 4)
            prev = curr
    return image


def get_lines(data):
    lines = []
    maxes = []
    for i, d in enumerate(data):
        o = np.where(d != 0)
        max_h, max_w = o[0].max(), o[1].max()
        maxes.append([i, max_w])
        lines.append(o)
    maxes = sorted(maxes, key=(lambda m: m[1]))
    return [lines[i] for i, _ in maxes]
