from utils import get_object_distance, scale
import cv2


class CarDetector:
    CAR_MIN_DISTANCE = 2
    AVG_CAR_WIDTH = 2.5
    cc = cv2.imread("../rsrc/cc.png")
    car_cascade_src = '../cars.xml'
    car_cascade = cv2.CascadeClassifier(car_cascade_src)

    def __init__(self, f, focal_length, ratio=1) -> None:
        self.f = f
        self.focal_length = focal_length
        self.ratio = ratio
        self.cars = []

    def detect(self, frame):
        self.safe = self.is_car_safe(frame)

    def is_car_in_front_close(self, distance):
        return distance < self.CAR_MIN_DISTANCE * 1000

    def detect_cars_in_front(self, frame):
        frame = scale(self.cc, size=frame.shape[:2][::-1])  # TODO
        return self.car_cascade.detectMultiScale(frame, 1.1, 1)

    def is_car_in_front(self, car):
        x, y, w, h = car
        return False

    def calculate_distance(self, car):
        x, y, w, h = car
        return get_object_distance(self.f, self.focal_length, w, self.AVG_CAR_WIDTH*1000, self.ratio)

    def is_car_safe(self, frame):
        self.cars = self.detect_cars_in_front(frame)
        for car in self.cars:
            if self.is_car_in_front(car):
                distance = self.calculate_distance(car)
                if self.is_car_in_front_close(distance):
                    return False
        return True

    def draw(self, frame):
        for (x, y, w, h) in self.cars:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return frame
