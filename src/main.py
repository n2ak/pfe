from utils_ import put_text, seek_video
from lane.ml_lane_detector import LaneDetector
from car import CarDetector
import cv2
import numpy as np
import time
from workers import *
from param import *
# from workers import LaneWorker, CarWorker, DrawWorker, lane_detect_one_frame, car_detect_one_frame, draw_main_window


def simple_on_danger(*x):
    print("Danger")


class Program:
    def __init__(
        self,
        lane_d: LaneDetector,
        car_d: CarDetector,
        use_async=False,
        frame_ratio=2,
        on_danger=simple_on_danger,
        draw=True,
        draw_lines=True,
    ) -> None:
        self.prev_time = time.time()-1
        self.use_async = use_async
        self.frame_ratio = frame_ratio
        self.on_danger = on_danger
        self.lane_d = lane_d
        self.car_d = car_d
        self.draw = draw
        self.draw_lines = draw_lines
        self.window_names = ["Main"]

        if use_async:
            self.init_workers()

        self.runner_func = self.run_worker
        if not use_async:
            spawn_params_window()
            self.runner_func = self.run_sync

    def init_workers(self):
        if self.draw:
            self.window_names.append("Perp")
            self.draw_worker = DrawWorker(self.frame_ratio, self.window_names)
            print("Waiting for draw to start")
        self.lane_worker = LaneWorker(self.lane_d)
        self.car_worker = CarWorker(self.car_d)
        # self.network = WebsocketWorker("0.0.0.0", 9999)

    def start(self):
        self.lane_worker.start()
        self.car_worker.start()
        # self.network.start()
        if self.draw:
            self.draw_worker.start()
    fps_ = []

    def stop(self):
        cv2.destroyAllWindows()
        if self.use_async:
            print("Stopping all workers")
            self.lane_worker.stop()
            self.car_worker.stop()
            # self.network.stop()
            if self.draw:
                self.draw_worker.stop()

    def run_worker(self, frame):
        l_w, c_w = self.lane_worker, self.car_worker
        f = frame.copy()
        c_w.q.put(("detect", frame))
        safe = c_w.q2.get()
        if safe:
            l_w.q.put(("detect", frame))

            l_w.q.put(("draw", frame))
            frame, lines = l_w.q2.get()
            print("shape", lines.shape)
        else:
            lines = np.zeros(frame.shape)
        c_w.q.put(("draw", frame))
        frame = c_w.q2.get()

        # self.network.q.put(frame)
        if self.draw:
            frames = [frame,]
            if self.draw_lines:
                frames.append(lines)
            self.draw_worker.q.put(frames)
            got = self.draw_worker.q2.get()
            return got is None
        return False

    def run_sync(self, frame):
        frame = car_detect_one_frame(self.car_d, frame)
        if self.car_d.safe:
            frame = lane_detect_one_frame(self.lane_d, frame)
            self.lane_d.lines
        if self.draw:
            if self.car_d.safe:
                frame = self.lane_d.draw(frame)
                if self.draw_lines:
                    show_window("Perp", self.lane_d.lines, 2)
            frame = self.car_d.draw(frame)
            self.update_fps(frame)
            draw_main_window(frame, self.frame_ratio)
            return bool(cv2.waitKey(1) & 0xFF == ord('q'))
        return False

    def run(self, video):
        if self.use_async:
            self.start()
        try:
            while True:
                self.on, frame = video.read()
                if not self.on:
                    break
                if self.runner_func(frame):
                    break
        except KeyboardInterrupt:
            pass
        self.stop()

    def update_fps(self, frame):
        new = time.time()
        self.fps_.append(1//(new-self.prev_time))
        self.fps_ = self.fps_[-10:]
        # print(self.fps_)
        fps = np.mean(self.fps_)
        self.prev_time = new
        text = f"FPS: {int(fps)}"
        put_text(frame, text, (7, 90), thickness=2)
        return frame
