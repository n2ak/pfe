from __future__ import annotations
from .params import ObjectDetectorParams
from src.utils import get_object_distance, get_object_distance2, draw_text_with_backgraound
from src.yolo import Yolo
import cv2
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from src.drawer import DrawParams


class ObjectInfo():
    def __init__(self, type, distance, coords) -> None:
        self.type = type
        self.distance = distance
        self.coords = coords


class ObjectDetector:
    OBJECTS_WIDTH: dict[str, float] = {
        "car": 1.8,
        "truck": 2.5,
        "bus": 2.5,
    }

    def __init__(self, params: ObjectDetectorParams, ratio=1, objects: List[str] = []) -> None:
        self.objects_to_detect = ["car", "truck", "bus"]
        self.objects_to_detect.extend(objects)
        # assert params.yolo_version in ["YOLOv5n.pt", "YOLOv8n.pt"]
        for o in self.objects_to_detect:
            assert o in self.OBJECTS_WIDTH.keys(), f"No width for {o}."

        self.model = Yolo(params.WEIGHTS, hub=False)
        self.safe = True
        self.close_objects: List[ObjectInfo] = []
        # assert os.path.exists("../yolov5") and os.path.isdir("../yolov5")

        self.params = params
        print("Object", id(self.params))
        self._ready = False

    def init(self, initial_frame):
        h, w = initial_frame.shape[-1]
        self.params.FRAME_CENTER_Y = w//2

    def detectable(self, type):
        return (type in self.objects_to_detect)

    def is_object_in_front_close(self, distance):
        # print(2, "self.params.CAR_MIN_DISTANCE", self.params.CAR_MIN_DISTANCE)
        return distance < self.params.CAR_MIN_DISTANCE * 1000

    def estimated_object_width(self, type):
        # assert type in self.OBJECTS_WIDTH.keys()
        return self.OBJECTS_WIDTH[type]

    def is_object_in_front(self, object: ObjectInfo):
        # return True
        x, y, w, h = object.coords
        center_y = int(x+w//2)
        offset = 100
        c_y = self.params.FRAME_CENTER_Y
        in_front = (c_y - offset) < center_y < (c_y + offset)
        # # TODO :add check
        # if in_front and (y+h) > (720-150):
        #     print("y+h", y+h)
        return in_front

    def calculate_distance(self, object: ObjectInfo):
        (x, y, w, h), type = object.coords, object.type
        f = self.params.F
        real_width = self.estimated_object_width(type) * 1000
        return get_object_distance2(f, w, real_width)
        # return get_object_distance(f, 4.74, w, real_width, 1)

    def calculate_distances(self, objects):
        distances = []
        for object in objects:
            distance = self.calculate_distance(object)
            distances.append(distance)
        return distances

    def is_car_safe(self, frame):
        objects = self.detect_objects_in_front(frame)
        distances = self.calculate_distances(objects)
        self.close_objects = []
        for object, distance in zip(objects, distances):
            distance = None
            if self.is_object_in_front(object):
                distance = self.calculate_distance(object)
                object.distance = distance
                if self.is_object_in_front_close(distance):
                    self.close_objects.append(object)
        return len(self.close_objects) == 0

    def detect_objects_in_front(self, frame, return_distances=True):
        results = self.model.predict(frame)
        objects: List[ObjectInfo] = []
        for cls, object in zip(results.boxes.cls, results.boxes.xyxy.int().tolist()):
            (x, y, w, h),  name = object, results.names[cls.item()]
            if not self.detectable(name):
                continue
            if return_distances:
                w = w - x
                h = h - y
            objects.append(
                ObjectInfo(
                    name,
                    -1,
                    (x, y, w, h),
                ),
            )

        return objects

    def draw(self, frame, draw_params: DrawParams):
        if not self._ready:
            return frame
        # print(1, "self.params.CAR_MIN_DISTANCE", self.params.CAR_MIN_DISTANCE)
        if draw_params.RENDER_CAR_BOX:
            for object in self.close_objects:
                (x, y, w, h), name, distance = object.coords, object.type, object.distance
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
        return self.close_objects, self.safe

    def _update(self, data):
        self._ready = True
        if data is None:
            self._ready = False
            return
        self.close_objects, self.safe = data

    def is_safe(self):
        return self.safe
    # def ready(self):
    #     return len(self.close_objects) != 0
