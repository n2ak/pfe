from utils_ import get_object_distance, get_object_distance2, draw_text_with_backgraound
import cv2
from .params import CarParams
from yolo import Yolo

vehicule_classes = ["car", "truck", "bus"]


def is_vehicule(classes, c: str):
    return c.lower() in classes


class CarDetector:
    VEHICULE_WIDTH: dict[str, float] = {
        "car": 2.5,
        "truck": 3,
        "bus": 3,
    }

    def __init__(self, params: CarParams, ratio=1) -> None:
        assert params.yolo_version in ["yolov5", "yolov8"]

        self.model = Yolo(params.yolo_version)
        self.safe = True
        self.close_cars = []
        # assert os.path.exists("../yolov5") and os.path.isdir("../yolov5")

        self.params = params
        self._ready = False

    def is_car_in_front_close(self, distance):
        return distance < self.params.car_min_distance * 1000

    def detect_cars_in_front(self, frame, return_distances=True):
        results = self.model.detect(frame)
        cars = []
        for car in results.pandas().xyxy[0].to_numpy():
            x, y, xmax, ymax, conf, c, name = car
            if not is_vehicule(vehicule_classes, name):
                continue
            x, y, xmax, ymax = int(x), int(y), int(xmax), int(ymax)
            # cv2.rectangle(frame, (x, y), (xmax, ymax), (255, 0, 0), 2)
            if return_distances:
                xmax = xmax - x
                ymax = ymax - y
            cars.append((x, y, xmax, ymax, name))
        return cars

    def estimated_vehicule_width(self, car_name):
        assert car_name in self.VEHICULE_WIDTH.keys()
        return self.VEHICULE_WIDTH[car_name]

    def is_car_in_front(self, car):
        # return True
        x, y, w, h, name = car
        center_y = int(x+w//2)
        offset = 100
        c_y = self.params.frame_center_y
        in_front = (c_y - offset) < center_y < (c_y + offset)
        # # TODO :add check
        # if in_front and (y+h) > (720-150):
        #     print("y+h", y+h)
        return in_front

    def calculate_distance(self, car):
        x, y, w, h, name = car
        f = self.params.f
        real_width = self.estimated_vehicule_width(name)*1000
        return get_object_distance2(f, w, real_width)
        return get_object_distance(f, self.focal_length, w, real_width, self.params.ratio)

    def calculate_distances(self, cars):
        distances = []
        for car in cars:
            distance = self.calculate_distance(car)
            distances.append(distance)
        return distances

    def is_car_safe(self, frame):
        cars = self.detect_cars_in_front(frame)
        distances = self.calculate_distances(cars)
        self.close_cars = []
        safe = True
        for car, distance in zip(cars, distances):
            distance = None
            if self.is_car_in_front(car):
                distance = self.calculate_distance(car)
                if self.is_car_in_front_close(distance):
                    self.close_cars.append((*car, distance))
                    safe = False
        return safe

    # def draw(self, frame, close_cars):
    #     return self.model.draw(frame, close_cars)

    def draw(self, frame):
        if not self._ready:
            return frame
        for x, y, w, h, name, distance in self.close_cars:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            distance = int(distance)
            distance_type = self.distance_type(distance)
            draw_text_with_backgraound(
                frame, f"{name} - {(distance/1000):.1f}m \n{distance_type}", x, y)
        return frame

    def distance_type(self, distance):
        if distance < 15_000:
            return "very close"
        if distance < 30_000:
            return "close"

    def detect(self, frame):
        self.safe = self.is_car_safe(frame)
        return self.close_cars, self.safe

    def _update(self, data):
        self._ready = True
        if data is None:
            self._ready = False
            return
        self.close_cars, self.safe = data

    # def ready(self):
    #     return len(self.close_cars) != 0
