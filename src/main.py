from threading import Thread
from multiprocessing import Pool, Queue, Process
from lane_detector import LaneDetector
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from car import CarDetector


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
    ) -> None:
        self.lane_d = lane_d
        self.car_d = car_d
        self.prev_time = time.time()-1
        self.use_async = use_async
        self.frame_ratio = frame_ratio
        self.on_danger = on_danger

    def stop(self):
        cv2.destroyAllWindows()
    fps_ = []

    def update_fps(self, frame):
        new = time.time()
        self.fps_.append(1//(new-self.prev_time))
        self.fps_ = self.fps_[-10:]
        # print(self.fps_)
        fps = np.mean(self.fps_)
        self.prev_time = new
        text = f"FPS: {int(fps)}"
        self.lane_d.put_text(frame, text, (7, 90), thickness=2)

    def run(self, video, pool):
        while True:
            self.on, frame = video.read()
            if self.on:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # s = time.time()
                if self.use_async:
                    lane = pool.apply_async(self.tick, args=(frame.copy(),))
                    car = pool.apply_async(self.detect_cars,
                                           args=(frame.copy(),))
                    self.lane_d = lane.get()
                    self.car_d = car.get()
                else:
                    self.tick(frame)
                    self.detect_cars(frame)
                # print(1/(time.time()-s))

                self.update_fps(frame)
                frame = self.draw_main_frame(frame)
                self.lane_d.show_window("Main window", frame, self.frame_ratio)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break
            else:
                self.stop()
                break

    def detect_cars(self, frame):
        print("detect_cars")
        self.car_d.detect(frame)
        return self.car_d

    # def detect_cars(self, frame):
    #

    def tick(self, frame):
        print("ticking")
        self.lane_d.pipeline(frame)
        is_in_lane = self.lane_d.is_in_lane()
        self.fps = 1
        self.lane_d.put_text(
            frame, f"In lane: {bool(is_in_lane)}", (7, 50), thickness=2)
        return self.lane_d

    def draw_main_frame(self, frame):
        frame = self.lane_d.draw(frame)
        frame = self.car_d.draw(frame)
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
    # p.start()
    # p.run()
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

    def danger(cause):
        print("Danger", cause)
    car_d = CarDetector(F, FOCAL_LENGTH)
    ld.init_polygon(config)

    p = Program(ld, car_d, use_async=True, frame_ratio=2)

    pool = Pool(6)
    p.run(video, pool)
    pool.close()
    pool.join()


if __name__ == "__main__":
    test()
