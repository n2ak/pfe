from utils import put_text
from lane_detector import LaneDetector
from car import CarDetector
import cv2
import numpy as np
import time
from workers import LaneWorker, CarWorker, DrawWorker, lane_detect_one_frame, car_detect_one_frame, draw_main_window


def simple_on_danger(*x):
    print("Danger")


# class WindowWorker():


class Program:
    def __init__(
        self,
        lane_d: LaneDetector,
        car_d: CarDetector,
        use_async=False,
        frame_ratio=2,
        on_danger=simple_on_danger,
        draw=True
    ) -> None:
        self.prev_time = time.time()-1
        self.use_async = use_async
        self.frame_ratio = frame_ratio
        self.on_danger = on_danger
        self.lane_d = lane_d
        self.car_d = car_d
        self.draw = draw

        if use_async:
            self.init_workers()

        self.runner_func = self.run_sync if not self.use_async else self.run_worker

    def init_workers(self):
        self.lane_worker = LaneWorker(self.lane_d)
        self.car_worker = CarWorker(self.car_d)
        if self.draw:
            self.draw_worker = DrawWorker(self.frame_ratio)

    def start(self):
        self.lane_worker.start()
        self.car_worker.start()
        if self.draw:
            self.draw_worker.start()

    fps_ = []

    def stop(self):
        cv2.destroyAllWindows()
        if self.use_async:
            print("Stopping all workers")
            self.lane_worker.stop()
            self.car_worker.stop()
            if self.draw:
                self.draw_worker.stop()

    def run_worker(self, frame):
        l_w, c_w = self.lane_worker, self.car_worker
        f = frame.copy()
        l_w.q.put(("detect", frame))
        c_w.q.put(("detect", frame))

        l_w.q.put(("draw", frame))
        frame = l_w.q2.get()
        c_w.q.put(("draw", frame))
        frame = c_w.q2.get()

        if self.draw:
            self.draw_worker.q.put(frame)
            got = self.draw_worker.q2.get()
            return got is None
        return False

    def run_sync(self, frame):
        frame = lane_detect_one_frame(self.lane_d, frame)
        frame = car_detect_one_frame(self.car_d, frame)
        if self.draw:
            frame = self.lane_d.draw(frame)
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
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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


def test():
    F = 2800
    FOCAL_LENGTH = 4.74
    config = {
        "polygon_height": 180,
        "lane_center1": 720,
        "lane_width1": 70*2,
        "lane_center2": 700,
        "lane_width2": 380*2,
    }
    src = "../rsrc/video2.mp4"
    video = cv2.VideoCapture(src)
    ld = LaneDetector(
        (720, 1280),
        use_bitwise=True,
        draw_roi=True,
        show_perp_lines=True,
        color_threshold=180,
        window_size_ratio=2,
        use_canny=True,
        canny_thresholds=(70, 100)
    )
    car_d = CarDetector(F, FOCAL_LENGTH)
    ld.init_polygon(config)
    p = Program(
        ld,
        car_d,
        use_async=False,
        frame_ratio=2,
        draw=True
    )
    p.run(video)
    time.sleep(1)
    print("Exited")
    import sys
    sys.exit(0)


if __name__ == "__main__":
    test()
