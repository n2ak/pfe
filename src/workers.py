from utils import show_window, put_text
from multiprocessing import Queue, Process

from lane_detector import LaneDetector
from car import CarDetector
import time
import cv2
import numpy as np


class Worker:
    def __init__(self, target, args=()) -> None:
        self.q = Queue()
        args = (self.q, *args)
        self.target = target
        self.p = Process(target=self.main, args=args)
        self.p.daemon = True

    def main(self, *args):
        print("**** Started", self.__class__.__name__)
        try:
            import signal
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.target(*args)
        except:
            pass
        print("**** Stopped", self.__class__.__name__)

    def start(self):
        self.p.start()

    def stop(self):
        self.q.put(None)
        pass


class LaneWorker(Worker):
    def __init__(self, lane_d: LaneDetector) -> None:
        self.q2 = Queue()
        self.detector = lane_d
        self.w = super().__init__(self.tick, args=(self.q2,))

    def tick(self, q: Queue, q2: Queue):
        while True:
            s = time.time()
            got = q.get()
            if got is None:
                break
            action, frame = got
            # print("LaneWorker", "Got action:", action)
            if action == "detect":
                frame = self.detect(self.detector, frame)
            elif action == "draw":
                frame = self.draw(self.detector, frame)
                q2.put(frame)
            else:
                raise str(action) + " not recognized"
            # print("lane Done in:", s, time.time()-s)

    def detect(self, d, frame):
        return lane_detect_one_frame(d, frame)

    def draw(self, d: LaneDetector, frame):
        return d.draw(frame)


class DrawWorker(Worker):
    def __init__(self, frame_ratio) -> None:
        self.q2 = Queue()
        self.prev_time = time.time()-1
        self.frame_ratio = frame_ratio
        super().__init__(target=self.draw, args=(self.q2,))

    def draw(self, q: Queue, q2: Queue):
        # ld_ =
        while True:
            got = q.get()
            s = time.time()
            if got is None:
                break
            frame = got
            # print("Drawing")
            self.update_fps(frame)
            draw_main_window(frame, self.frame_ratio)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                q2.put(None)
            q2.put("www")
            # print("Car Done in:", s, time.time()-s)

    fps_ = []

    def update_fps(self, frame):
        new = time.time()
        self.fps_.append(1//(new-self.prev_time))
        self.fps_ = self.fps_[-10:]
        # print(self.fps_)
        fps = np.mean(self.fps_)
        self.prev_time = new
        text = f"FPS: {int(fps)}"
        put_text(frame, text, (7, 90), thickness=2)


class CarWorker(Worker):
    def __init__(self, car_d: CarDetector) -> None:
        self.detector = car_d
        self.q2 = Queue()
        self.w = super().__init__(self.tick, args=(self.q2,))

    def tick(self, q: Queue, q2: Queue):
        while True:
            got = q.get()
            if got is None:
                break
            action, frame = got
            # print("CarWorker", "Got action:", action)
            if action == "detect":
                frame = self.detect(self.detector, frame)
            elif action == "draw":
                frame = self.draw(self.detector, frame)
                q2.put(frame)

    def detect(self, d, frame):
        return car_detect_one_frame(d, frame)

    def draw(self, d: CarDetector, frame):
        return d.draw(frame)


def draw_main_window(frame, fr):
    show_window("Main window", frame, fr)


def lane_detect_one_frame(detector: LaneDetector, frame):
    detector.pipeline(frame)
    is_in_lane = detector.is_in_lane()
    detector.put_text(
        frame, f"In lane: {bool(is_in_lane)}", (7, 50), thickness=2)
    return frame


def car_detect_one_frame(detector: CarDetector, frame):
    detector.detect(frame)
    return frame
