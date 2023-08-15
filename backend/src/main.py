# TODO : draw nothing when no lanes are detected for to many frames


from server import Server
from multiprocessing import Queue, Process
from utils_ import read_video
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
        server: Server,
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
        self.server = server

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

    def run_sync(self, frame):
        # car_data, lane_data = None, None
        if self._worker_free is True:
            # print("="*10, "frame", type(frame))
            self.detectionWorker.q_in.put(frame)
            self._worker_free = False
        # ret = False
        if not self.detectionWorker.q_out.empty():
            car_data, lane_data = self.detectionWorker.q_out.get()
            self.car_d._update(car_data)
            self.lane_d._update(lane_data)
            self._worker_free = True
        if self.draw:
            # print("Drawwing")
            frame = self.drawer.draw(
                frame,
                self.car_d,
                self.lane_d,
            )
        return frame

    def run(self, video, frame_count):
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

                self.on, frame = read_video(video, )  # size=(640, 384))
                if not self.on:
                    break
                frame = self.runner_func(frame)
                # if off:
                #     break
                cv2.imshow("sss", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                Server.set_frame(frame)
                time.sleep(1/frame_count)

            time.sleep(.1)
        except KeyboardInterrupt:
            pass
        self.detectionWorker.stop()
        self.stop()

    def run_as_thread(self, video, fps):
        import threading
        t = threading.Thread(target=self.run, args=(video, fps,))
        t.daemon = True
        t.start()

    def run_server(self, host, port):
        Server.run_server(host, port)

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
        self.q_in = Queue()
        self.q_out = Queue()
        args = (self.q_in, self.q_out, *args)
        self.p = Process(target=self.main, args=args)
        self.p.daemon = True
        self.car_detecor, self.lane_detector = car_d, lane_d

    def main(self, q_in: Queue, q_out: Queue):
        car_detecor, lane_detector = self.car_detecor, self.lane_detector
        # print("="*20, "Started Worker")
        i = 0
        q_out.put("Started")
        car_data = None
        lane_data = None
        while True:
            i += 1
            in_ = q_in.get()
            if in_ is None:
                break
            frame = in_
            car_data = car_detecor.detect(frame)
            if (car_detecor is not None) and car_detecor.safe:
                lane_data = lane_detector.pipeline(frame)
            q_out.put((car_data, lane_data))

            time.sleep(.05)
            if (i % 100) == 0:
                print(f"{i} elements were processed")

    def start(self):
        self.p.start()

    def stop(self):
        self.q_in.put(None)
        self.p.kill()
