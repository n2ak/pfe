from utils_ import put_text, draw_text_with_backgraound, car_detect_one_frame, lane_detect_one_frame, show_window, draw_main_window
from lane import LaneDetectorBase
from car import CarDetector
import cv2
import numpy as np
import time
from param import *
from drawer import Drawer
# from workers import LaneWorker, CarWorker, DrawWorker, lane_detect_one_frame, car_detect_one_frame, draw_main_window


def simple_on_danger(*x):
    print("Danger")


MAX = 9_000_000


class Program:
    fps_ = [0]

    def __init__(
        self,
        lane_d: LaneDetectorBase,
        car_d: CarDetector,
        drawer: Drawer,
        use_async=False,
        frame_ratio=2,
        on_danger=simple_on_danger,
        draw=True,
        draw_lines=True,
        show_windows=False,
    ) -> None:
        self.use_async = use_async
        self.frame_ratio = frame_ratio
        self.on_danger = on_danger
        self.lane_d = lane_d
        self.drawer = drawer
        self.car_d = car_d
        self.draw = draw
        self.draw_lines = draw_lines
        self.show_windows = show_windows
        self.window_names = ["Main"]

        if use_async:
            self.init_workers()

        if not use_async:
            self.runner_func = self.run_sync

    def start(self):
        self.lane_worker.start()
        self.car_worker.start()

    def stop(self):
        if self.use_async:
            print("Stopping all workers")
            self.lane_worker.stop()
            self.car_worker.stop()
            self.network.stop()
            if self.draw:
                self.draw_worker.stop()
        # self.detectionWorker.p.close()
        cv2.destroyAllWindows()

    def forward_to_server(self, frame):
        from server import set_frame
        set_frame(frame)

    def run_sync(self, frame):
        if self._worker_free is True:
            # print("="*10, "frame", type(frame))
            self.detectionWorker.q_in.put(frame)
            self._worker_free = False
        ret = False
        if not self.detectionWorker.q_out.empty():
            (self.cars, self.cars_safe), (self.lanes,
                                          self.lanes_safe) = self.detectionWorker.q_out.get()
            self._worker_free = True
        if self.draw:
            frame = self.drawer.draw(
                frame,
                self.car_d,
                self.lane_d,
                self.cars,
                self.cars_safe,
                self.lanes,
                self.lanes_safe
            )
        self.forward_to_server(frame)
        time.sleep(1/30)
        return ret

    def run(self, video):
        (self.cars, self.cars_safe) = ([], True)
        (self.lanes, self.lanes_safe) = (None, True)
        if self.use_async:
            self.start()
        else:
            self.detectionWorker = DetectionWorker(
                self.car_d,
                self.lane_d
            )
            self.detectionWorker.start()
            assert self.detectionWorker.q_out.get() == "Started"
            self._worker_free = True
        try:
            i = 0
            while True:
                i += 1
                if i > MAX:
                    print("="*10, f"${MAX} iters was reached.")
                    import sys
                    sys.exit()
                    break
                self.on, frame = video.read()
                if not self.on:
                    break
                if self.runner_func(frame):
                    break
            time.sleep(.1)
        except KeyboardInterrupt:
            pass
        self.detectionWorker.stop()
        self.stop()

    def run_as_thread(self, video):
        import threading
        t = threading.Thread(target=self.run, args=(video,))
        t.daemon = True
        t.start()

    def run_server(self, host, port):
        from server import run_server
        run_server(host, port)

    # def init_workers(self):
    #     from workers import DrawWorker, LaneWorker, CarWorker
    #     if self.draw:
    #         self.window_names.append("Perp")
    #         self.draw_worker = DrawWorker(self.frame_ratio, self.window_names)
    #         print("Waiting for draw to start")
    #     self.lane_worker = LaneWorker(self.lane_d)
    #     self.car_worker = CarWorker(self.car_d)
        # self.network = WebsocketWorker("0.0.0.0", 9999)

    # def run_worker(self, frame):
    #     l_w, c_w = self.lane_worker, self.car_worker
    #     f = frame.copy()
    #     c_w.q.put(("detect", frame))
    #     safe = c_w.q2.get()
    #     if safe:
    #         l_w.q.put(("detect", frame))

    #         l_w.q.put(("draw", frame))
    #         frame, lines = l_w.q2.get()
    #         print("shape", lines.shape)
    #     else:
    #         lines = np.zeros(frame.shape)
    #     c_w.q.put(("draw", frame))
    #     frame = c_w.q2.get()

    #     # self.network.q.put(frame)
    #     if self.draw:
    #         frames = [frame,]
    #         if self.draw_lines:
    #             frames.append(lines)
    #         self.draw_worker.q.put(frames)
    #         got = self.draw_worker.q2.get()
    #         return got is None
    #     return False


class DetectionWorker:
    def __init__(self, car_d: CarDetector, lane_d: LaneDetectorBase, args=()) -> None:
        from multiprocessing import Queue, Process
        self.q_in = Queue()
        self.q_out = Queue()
        args = (self.q_in, self.q_out, *args)
        self.p = Process(target=self.main, args=args)
        self.p.daemon = True
        self.car_detecor, self.lane_detector = car_d, lane_d

    def main(self, q_in, q_out):
        car_detecor, lane_detector = self.car_detecor, self.lane_detector
        # print("="*20, "Started Worker")
        i = 0
        q_out.put("Started")
        while True:
            i += 1
            in_ = q_in.get()
            if in_ is None:
                break
            frame = in_
            car_detect_one_frame(car_detecor, frame)
            if (car_detecor is not None) and car_detecor.safe:
                pass
                lane_detect_one_frame(lane_detector, frame)
            q_out.put(
                (
                    (car_detecor.close_cars, car_detecor.safe),
                    (lane_detector.lanes, lane_detector.safe)
                )
            )
            time.sleep(.05)
            if (i % 100) == 0:
                print(f"{i} elements were processed")

    def start(self):
        self.p.start()

    def stop(self):
        self.q_in.put(None)
        self.p.kill()
