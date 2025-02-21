from src.adas.detectors.lane.params import YoloLaneDetecorParams
import numpy as np
import cv2
from src.utils import draw_lane_zone, polynome
from src.base.lane_detector import LaneDetectorBase
from src.components.drawer import DrawParams

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class YoloModel:
    def __init__(self, version: str, hub=True) -> None:
        if hub is True:
            version = version.lower()
            self.model = load_yolo(version, "../")
        else:
            from ultralytics import YOLO
            self.model = YOLO(version,)

    def detect(self, frame, **kwargs):
        return self.model(frame, **kwargs)

    def predict(self, frame, verbose=False, **kwargs):
        if isinstance(frame, str):
            from src.utils import read_rgb
            frame = read_rgb(frame)
        result = self.model.predict(frame, verbose=verbose)
        return result[0]


def load_yolo(version: str, base=None):
    import torch
    if base is not None:
        torch.hub.set_dir(base)
    return torch.hub.load(f'ultralytics/{version}', f'{version}s')


class YoloLaneDetecor(LaneDetectorBase):

    def __init__(
        self,
        params: YoloLaneDetecorParams,
    ) -> None:
        super().__init__()
        self.model = YoloModel(params.WEIGHTS.value(), hub=False)
        self.lane = None

        self._ready = False
        self.in_lane = True
        self.pos = None
        self.params = params

    def init(self, initial_frame):
        h, w = initial_frame.shape[:2]
        offset = int(h * .8)

        self.params.CAR_CENTER.set_value(w//2)
        self.params.POLY_OFFSET.set_value(offset)

    def draw(self, frame, draw_params: DrawParams):
        render_lines = draw_params.RENDER_LINES.value()
        render_lane = draw_params.RENDER_LANE.value()
        render_center = draw_params.RENDER_CENTER
        car_center = self.params.CAR_CENTER.value()
        lane_threshold = self.params.LANE_THRESHOLD.value()
        line_n_points = draw_params.LANE_N_POINTS.value()

        h, w = frame.shape[:2]
        if not self._ready:
            return frame

        left, right, ys = self.left, self.right, self.ys
        left = scale(left, w)
        right = scale(right, w)
        ys = scale(ys, h)

        left_lane, right_lane, height = left[-1], right[-1], ys[-1]
        self.pos, in_lane = lane_departure_warning(
            left_lane,
            right_lane,
            car_center,
            lane_threshold,
        )
        self.in_lane = in_lane
        out = frame
        step = round(len(left) / line_n_points)
        if step == 0:
            step = len(left)
        if render_lane:
            out = draw_lane_zone_transp(
                out, left, right, ys, opacity=.30, step=step)
            out = (out*255).astype(int)
        if render_lines:
            out = draw_lines(out, left, right, ys, step=step,
                             line_color=RED)

        if render_center:
            lane_center = (left_lane + right_lane) // 2

            ccr = car_center+lane_threshold
            ccl = car_center-lane_threshold
            ht = h - 40
            hm = h - 50
            hb = h - 60

            cv2.line(out, (ccr, hm), (ccl, hm), GREEN, 3)
            cv2.line(out, (ccr, hb), (ccr, ht), GREEN, 3)
            cv2.line(out, (ccl, hb), (ccl, ht), GREEN, 3)
            cv2.circle(out, (car_center, hm), 5, GREEN, -1)

            c = GREEN if in_lane else BLUE
            cv2.circle(out, (lane_center, height), 6, c, -1)
        return out

    def pipeline(self, frame):
        use_poly_offset = self.params.USE_POLY_FIT.value()
        use_poly_fit = self.params.USE_POLY_FIT.value()
        poly_offset = self.params.POLY_OFFSET.value()
        res = self.model.predict(frame)
        if res.masks is None:
            return None
        lines = get_lines(res.masks.data[:3])
        mask = np.zeros(frame.shape[:2])

        colors = [3, 2, 1]
        for i, o in enumerate(lines):
            draw_masks_on_image(mask, [zip(*o[::-1])], color=colors[i])

        left, right, ys, dirs = get_curvatures2(mask, [1, 2], 1, range=[0, -1])

        if len(left) == 0 or len(right) == 0:
            return None

        if use_poly_fit:
            deg = 2
            ys = np.array(ys)
            ys2 = ys
            if use_poly_offset:
                ys2 = np.linspace(
                    ys.min(), poly_offset, 50, dtype=int)

            def fit(ind):
                ind = np.polyfit(ys, ind, deg)
                ind = polynome(ind, ys2)
                ind = ind.astype(int)
                return ind
            left = fit(left)
            right = fit(right)
            ys = ys2

        H, W = res.masks.data[0].shape
        # left_lane, right_lane, height = left[-1], right[-1], ys[-1]
        left = normalize(left, W)
        right = normalize(right, W)
        ys = normalize(ys, H)

        # left_lane, right_lane, height = left[-1], right[-1], ys[-1]

        return left, right, ys, None

    def is_in_lane(self):
        return self.in_lane

    def _update(self, data):
        self._ready = True
        if data is None:
            self._ready = False
            return
        self.left, self.right, self.ys, _ = data

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
    if isinstance(var, (list, np.ndarray)):
        return [int(var[i]*to) for i in range(len(var))]
    return int(var*to)


def draw_lane_zone_transp(image, left, right, ys, opacity=.75, lane_color=(0, 1, 0), step=5):
    mask = draw_lane_zone(np.zeros_like(image), (right, left),
                          ys, step=step).astype(np.float64)
    mask /= 255.0
    mask *= opacity
    green = np.ones(image.shape, dtype=np.float64)*lane_color
    green = green*mask + (image/255)*(1.0-mask)
    return green


def draw_lines(image, left, right, ys, step=5, line_color=(0, 0, 255), thickness=3):
    prev = None
    for r, l, y in list(zip(right, left, ys))[::step]:
        if prev is not None:
            cv2.line(image, (l, y), prev[1], line_color, thickness=thickness)
            cv2.line(image, (r, y), prev[0], line_color, thickness=thickness)
        prev = [r, y], [l, y]
    return image


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
        if len(o[1]) == 0:
            continue
        max_w = o[1].max()
        maxes.append([i, max_w])
        lines.append(o)
    maxes = sorted(maxes, key=(lambda m: m[1]))
    return [lines[i] for i, _ in maxes]
