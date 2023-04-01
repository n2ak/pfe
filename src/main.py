from threading import Thread
from multiprocessing import Pool, Queue, Process
from lane_detector import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

# def w(i):
#     time.sleep(i)


class Program:
    def __init__(
        self,
        lane_d: LaneDetector,
        car_d,
        use_async=False,
        frame_ratio=2,
        on_danger=lambda *x: print("Danger"),
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
                # s = time.time()
                if self.use_async:
                    a = pool.apply_async(self.tick, args=(frame,))
                    # b = pool.apply_async(self.detect_cars, args=(frame,))
                    frame = a.get()
                    # b.get()
                else:
                    frame = self.tick(frame)
                    # self.detect_cars(frame)
                # print(1/(time.time()-s))

                self.update_fps(frame)
                self.lane_d.show_window("Main window", frame, self.frame_ratio)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break
            else:
                self.stop()
                break
    # cc = cv2.imread("cc.png")
    # car_cascade_src = 'cars.xml'
    # car_cascade = cv2.CascadeClassifier(car_cascade_src)

    # def detect_cars(self, frame):
    #     for a in range(5):
    #         cars = self.car_cascade.detectMultiScale(self.cc, 1.1, 1)
    #         for (x, y, w, h) in cars:
    #             cv2.rectangle(self.cc, (x, y), (x+w, y+h), (255, 0, 0), 2)
    #     return frame

    def tick(self, frame):
        # print("t")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = self.lane_d.pipeline(frame)
        is_in_lane = self.lane_d.is_in_lane()
        self.fps = 1
        self.lane_d.put_text(
            frame, f"In lane: {bool(is_in_lane)}", (7, 50), thickness=2)
        return frame


if __name__ == "__main__":
    # p.start()
    # p.run()
    config = {
        "polygon_height": 180,
        "lane_center1": 720,
        "lane_width1": 70*2,
        "lane_center2": 700,
        "lane_width2": 380*2,
    }

    src = "./rsrc/video2.mp4"
    video = cv2.VideoCapture(src)
    ld = LaneDetector(
        (720, 1280),
        use_bitwise=True,
        draw_roi=True,
        show_perp_lines=False,
        color_threshold=180,
        window_size_ratio=2,
        use_canny=False,
        canny_thresholds=(70, 100)
    )
    ld.init_polygon(config)
    p = Program(ld, None, use_async=True)

    pool = Pool(6)
    p.run(pool)
