from utils_ import get_object_distance, load_yolo, draw_text_with_backgraound
import cv2
import torch
import os

vehicule_classes = ["car", "truck", "bus"]


def is_vehicule(classes, c: str):
    return c.lower() in classes


class CarDetector:
    CAR_MIN_DISTANCE = 30
    AVG_CAR_WIDTH = 2.5

    # cc = cv2.imread("../rsrc/cc.png")
    # car_cascade_src = '../cars.xml'
    # car_cascade = cv2.CascadeClassifier(car_cascade_src)

    VEHICULE_WIDTH: dict[str, float] = {
        "car": 2.5,
        "truck": 3,
        "bus": 3,
    }

    def __init__(self, f, focal_length, frame_center_y: int, ratio=1) -> None:
        self.f = f
        self.focal_length = focal_length
        self.ratio = ratio
        self.close_cars = []
        self.safe = True
        # assert os.path.exists("../yolov5") and os.path.isdir("../yolov5")
        self.model = Yolo("yolov5")
        self.frame_center_y = frame_center_y

    def detect(self, frame):
        self.safe = self.is_car_safe(frame)

    def is_car_in_front_close(self, distance):
        # print(distance, self.CAR_MIN_DISTANCE * 1000)
        return distance < self.CAR_MIN_DISTANCE * 1000

    # def detect_cars_in_front(self, frame):
    #     frame = scale(self.cc, size=frame.shape[:2][::-1])  # TODO
    #     return self.car_cascade.detectMultiScale(frame, 1.1, 1)
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
        in_front = (self.frame_center_y -
                    offset) < center_y < (self.frame_center_y + offset)
        # # TODO :add check
        # if in_front and (y+h) > (720-150):
        #     print("y+h", y+h)
        return in_front

    def calculate_distance(self, car):
        x, y, w, h, name = car
        return get_object_distance(self.f, self.focal_length, w, self.estimated_vehicule_width(name)*1000, self.ratio)

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

    def draw(self, frame, close_cars):
        return self.model.draw(frame, close_cars)


class Yolo:
    def __init__(self, version: str) -> None:
        version = version.lower()
        assert version in ["yolov5", "yolov8"]
        self.model = load_yolo(version, "../")

    def distance_type(self, distance):
        if distance < 15_000:
            return "very close"
        if distance < 30_000:
            return "close"

    def detect(self, frame):
        return self.model(frame)

    def draw(self, frame, close_cars):
        for x, y, w, h, name, distance in close_cars:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            distance = int(distance)
            distance_type = self.distance_type(distance)
            # background = np.zeros_like(frmae, dtype=np.uint8)

            draw_text_with_backgraound(
                frame, f"{name} - {(distance/1000):.1f}m \n{distance_type}", x, y)
        return frame
